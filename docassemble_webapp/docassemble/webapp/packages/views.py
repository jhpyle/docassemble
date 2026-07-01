import re
import packaging
from markupsafe import Markup
from flask import (
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from sqlalchemy import select
from docassemble_flask_user import login_required, roles_required
from docassemble.base.language.words import word
from docassemble.base.hooks import devel_login
from docassemble.webapp.config import GITHUB_BRANCH, DEFER, daconfig, START_TIME
from docassemble.webapp.extensions import db
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.helpers import file_set_attributes
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.filenames import secure_filename
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.helpers import (
    get_master_branch,
    get_package_info,
    install_git_package,
    install_pip_package,
    install_zip_package,
    redis_script,
    reset_process_running,
    should_run_create,
    summarize_results,
    uninstall_package,
    url_for,
    user_can_edit_package,
)
from docassemble.webapp.utils.helpers import version_warning
from .blueprint import packages_bp
from .forms import UpdatePackageForm
from .helpers import (
    get_branches_of_repo,
    get_package_name_from_zip,
    pypi_status,
)
from .models import Package

@packages_bp.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    setup_translation()
    if not current_app.config['ALLOW_UPDATES']:
        return ('File not found', 404)
    if not (current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin')):
        return ('File not found', 404)
    if 'taskwait' in session:
        del session['taskwait']
    if 'serverstarttime' in session:
        del session['serverstarttime']
    # pip.utils.logging._log_state = threading.local()
    # pip.utils.logging._log_state.indentation = 0
    if request.method == 'GET' and current_app.config['ENABLE_PLAYGROUND']:
        status = devel_login()
        if status:
            return status
    form = UpdatePackageForm(request.form)
    form.gitbranch.choices = [('', "Not applicable")]
    if form.gitbranch.data:
        form.gitbranch.choices.append((form.gitbranch.data, form.gitbranch.data))
    action = request.args.get('action', None)
    target = request.args.get('package', None)
    limitation = request.args.get('limitation', '')
    branch = None
    if action is not None and target is not None:
        package_list, package_auth = get_package_info()  # pylint: disable=unused-variable
        the_package = None
        for package in package_list:
            if package.package.name == target:
                the_package = package
                break
        if the_package is not None:
            if action == 'uninstall' and the_package.can_uninstall:
                uninstall_package(target)
            elif action == 'update' and the_package.can_update:
                existing_package = db.session.execute(select(Package).filter_by(name=target, active=True).order_by(Package.id.desc())).scalar()
                if existing_package is not None:
                    if limitation and existing_package.limitation != limitation:
                        existing_package.limitation = limitation
                        db.session.commit()
                    if existing_package.type == 'git' and existing_package.giturl is not None:
                        if existing_package.gitbranch:
                            install_git_package(target, existing_package.giturl, existing_package.gitbranch)
                        else:
                            install_git_package(target, existing_package.giturl, get_master_branch(existing_package.giturl))
                    elif existing_package.type == 'pip':
                        if existing_package.name == 'docassemble.webapp' and existing_package.limitation and not limitation:
                            existing_package.limitation = None
                            db.session.commit()
                        install_pip_package(existing_package.name, existing_package.limitation)
        result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', kwargs={'run_create': should_run_create(target)}))
        # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(target)))
        session['taskwait'] = result.id
        session['serverstarttime'] = START_TIME
        return redirect(url_for('packages.update_package_wait'))
    if request.method == 'POST' and form.validate_on_submit():
        # use_pip_cache = form.use_cache.data
        # pipe = r.pipeline()
        # pipe.set('da:updatepackage:use_pip_cache', 1 if use_pip_cache else 0)
        # pipe.expire('da:updatepackage:use_pip_cache', 120)
        # pipe.execute()
        if 'zipfile' in request.files and request.files['zipfile'].filename:
            try:
                the_file = request.files['zipfile']
                filename = secure_filename(the_file.filename)
                file_number = get_new_file_number(None, filename, None)
                saved_file = SavedFile(file_number, extension='zip', fix=True, should_not_exist=True)
                file_set_attributes(file_number, private=True, persistent=True, session=None, filename=None)
                zippath = saved_file.path
                the_file.save(zippath)
                saved_file.save()
                saved_file.finalize()
                pkgname = get_package_name_from_zip(zippath)
                if user_can_edit_package(pkgname=pkgname):
                    install_zip_package(pkgname, file_number)
                    result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', kwargs={"run_create": should_run_create(pkgname)}))
                    # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(pkgname)))
                    session['taskwait'] = result.id
                    session['serverstarttime'] = START_TIME
                    return redirect(url_for('packages.update_package_wait'))
                flash(word("You do not have permission to install this package."), 'error')
            except BaseException as err_mess:
                flash("Error of type " + str(type(err_mess)) + " processing upload: " + str(err_mess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip().rstrip('/')
                branch = form.gitbranch.data.strip()
                if not branch:
                    branch = get_master_branch(giturl)
                m = re.search(r'#egg=(.*)', giturl)
                if m:
                    packagename = re.sub(r'&.*', '', m.group(1))
                    giturl = re.sub(r'#.*', '', giturl)
                else:
                    packagename = re.sub(r'/*$', '', giturl)
                    packagename = re.sub(r'^git+', '', packagename)
                    packagename = re.sub(r'#.*', '', packagename)
                    packagename = re.sub(r'\.git$', '', packagename)
                    packagename = re.sub(r'.*/', '', packagename)
                    packagename = re.sub(r'^docassemble-', 'docassemble.', packagename)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    install_git_package(packagename, giturl, branch)
                    result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', kwargs={"run_create": should_run_create(packagename)}))
                    #result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(packagename)))
                    session['taskwait'] = result.id
                    session['serverstarttime'] = START_TIME
                    return redirect(url_for('packages.update_package_wait'))
                flash(word("You do not have permission to install this package."), 'error')
            elif form.pippackage.data:
                pippackage = re.sub(r'@.*', '', form.pippackage.data).strip()
                m = re.match(r'([^>=<]+)([>=<]+.+)', pippackage)
                if m:
                    packagename = m.group(1)
                    limitation = m.group(2)
                else:
                    packagename = pippackage
                    limitation = None
                packagename = re.sub(r'[^A-Za-z0-9\_\-\.]', '', packagename)
                if user_can_edit_package(pkgname=packagename):
                    install_pip_package(packagename, limitation)
                    result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', kwargs={"run_create": should_run_create(packagename)}))
                    # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(packagename)))
                    session['taskwait'] = result.id
                    session['serverstarttime'] = START_TIME
                    return redirect(url_for('packages.update_package_wait'))
                flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to supply a Git URL, upload a file, or supply the name of a package on PyPI.'), 'error')
    package_list, package_auth = get_package_info()
    form.pippackage.data = None
    form.giturl.data = None
    initial_values = {
        "daDefaultBranch": branch if branch else 'null',
        "daGetGitBranches": url_for('packages.get_git_branches'),
        "daGithubBranch": GITHUB_BRANCH
    }
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename="app/update_package.min.js")}"></script>
    {redis_script(initial_values)}"""
    python_version = daconfig.get('python version', word('Unknown'))
    version = word("Current") + ': <span class="badge bg-primary">' + str(python_version) + '</span>'
    dw_status = pypi_status('docassemble.webapp')
    if daconfig.get('stable version', False):
        if not dw_status['error'] and 'info' in dw_status and 'releases' in dw_status['info'] and isinstance(dw_status['info']['releases'], dict):
            stable_version = packaging.version.parse('1.1')
            latest_version = None
            for version_number, version_info in dw_status['info']['releases'].items():  # pylint: disable=unused-variable
                version_number_loose = packaging.version.parse(version_number)
                if version_number_loose >= stable_version:
                    continue
                if latest_version is None or version_number_loose > packaging.version.parse(latest_version):
                    latest_version = version_number
            if latest_version != str(python_version):
                version += ' ' + word("Available") + ': <span class="badge bg-success">' + latest_version + '</span>'
    else:
        if not dw_status['error'] and 'info' in dw_status and 'info' in dw_status['info'] and 'version' in dw_status['info']['info'] and dw_status['info']['info']['version'] != str(python_version):
            version += ' ' + word("Available") + ': <span class="badge bg-success">' + dw_status['info']['info']['version'] + '</span>'
    allowed_to_upgrade = current_user.has_role('admin') or user_can_edit_package(pkgname='docassemble.webapp')
    if daconfig.get('stable version', False):
        limitation = '<1.1'
    else:
        limitation = ''
    if daconfig.get('stable version', False):
        limitation = '<1.1.0'
    else:
        limitation = ''
    allowed_to_upgrade = current_user.has_role('admin') or user_can_edit_package(pkgname='docassemble.webapp')
    response = make_response(render_template('packages/update_package.html', version_warning=version_warning, bodyclass='daadminbody', form=form, package_list=sorted(package_list, key=lambda y: (0 if y.package.name == 'docassemble' or y.package.name.startswith('docassemble.') else 1, y.package.name.lower())), tab_title=word('Package Management'), page_title=word('Package Management'), extra_js=Markup(extra_js), version=Markup(version), allowed_to_upgrade=allowed_to_upgrade, limitation=limitation), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@packages_bp.route('/updatingpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_wait():
    setup_translation()
    if not (current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin')):
        return ('File not found', 404)
    next_url = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('packages.update_package')))
    my_csrf = generate_csrf()
    initial_values = {
        "daRestartAjax": url_for('main.restart_ajax'),
        "daCsrf": my_csrf,
        "daNoError": word("The package update did not report an error.  The logs are below."),
        "daErrorWithLog": word("The package update reported an error.  The logs are below."),
        "daUpdateError": word("There was an error updating the packages."),
        "daGeneralError": word("There was an error."),
        "daServerDidNotRespond": word("Server did not respond to request for update."),
        "daUrlUpdatePackageAjax": url_for('packages.update_package_ajax')
    }
    script = f"""
    <script{DEFER} src="{url_for('static', filename="app/updatingpackages.min.js")}"></script>
    {redis_script(initial_values)}"""
    response = make_response(render_template('packages/update_package_wait.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Updating'), page_title=word('Updating'), next_page=next_url), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@packages_bp.route('/get_git_branches', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def get_git_branches():
    if 'url' not in request.args:
        return ('File not found', 404)
    giturl = request.args['url'].strip()
    try:
        return jsonify({'success': True, 'result': get_branches_of_repo(giturl)})
    except BaseException as err:
        return jsonify({'success': False, 'reason': str(err)})


@packages_bp.route('/update_package_ajax', methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_ajax():
    if not (current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin')):
        return ('File not found', 404)
    if 'taskwait' not in session or 'serverstarttime' not in session:
        return jsonify(success=False)
    setup_translation()
    result = celery_app.AsyncResult(id=session['taskwait'])
    if result.ready():
        # if 'taskwait' in session:
        #     del session['taskwait']
        the_result = result.get()
        if the_result.__class__.__name__ == 'ReturnValue':
            if the_result.ok:
                # logmessage("update_package_ajax: success")
                if (hasattr(the_result, 'restart') and not the_result.restart) or (START_TIME > session['serverstarttime'] and not reset_process_running()):
                    if len(the_result.logmessages) > 210000:
                        the_result.logmessages = the_result.logmessages[0:100000] + "\n\nTRUNCATED\n\n" + the_result.logmessages[-100000:]
                    return jsonify(success=True, status='finished', ok=the_result.ok, summary=summarize_results(the_result.results, the_result.logmessages))
                return jsonify(success=True, status='waiting')
            if hasattr(the_result, 'error_message'):
                logmessage("update_package_ajax: failed return value is " + str(the_result.error_message))
                return jsonify(success=True, status='failed', error_message=str(the_result.error_message))
            if hasattr(the_result, 'results') and hasattr(the_result, 'logmessages'):
                if len(the_result.logmessages) > 210000:
                    the_result.logmessages = the_result.logmessages[0:100000] + "\n\nTRUNCATED\n\n" + the_result.logmessages[-100000:]
                return jsonify(success=True, status='failed', summary=summarize_results(the_result.results, the_result.logmessages))
            return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)))
        logmessage("update_package_ajax: failed return value is a " + str(type(the_result)))
        logmessage("update_package_ajax: failed return value is " + str(the_result))
        return jsonify(success=True, status='failed', error_message=str(the_result))
    return jsonify(success=True, status='waiting')
