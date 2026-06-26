import json
import re
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from sqlalchemy import select
from docassemble.base.functions import get_uid
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.config import START_TIME
from docassemble.webapp.utils.filenames import secure_filename
from docassemble.webapp.utils.helpers import (
    user_can_edit_package,
    install_pip_package,
    jsonify_task,
    get_package_info,
    install_git_package,
    uninstall_package,
    jsonify_with_status,
    should_run_create,
    true_or_false,
    get_master_branch,
    install_zip_package,
    reset_process_running,
    summarize_results,
)
from docassemble.webapp.extensions import db, csrf
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.files.helpers import file_set_attributes
from docassemble.webapp.daredis import r
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.utils.logger import logmessage
from .blueprint import packages_bp
from .helpers import get_package_name_from_zip
from .models import Package

@packages_bp.route('/api/package', methods=['GET', 'POST', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'HEAD'], automatic_options=True)
def api_package():
    if not api_verify(roles=['admin', 'developer'], permissions=['manage_packages']):
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        package_list, package_auth = get_package_info()  # pylint: disable=unused-variable
        packages = []
        for package in package_list:
            if not package.package.active:
                continue
            item = {'name': package.package.name, 'type': package.package.type, 'can_update': package.can_update, 'can_uninstall': package.can_uninstall}
            if package.package.packageversion:
                item['version'] = package.package.packageversion
            if package.package.giturl:
                item['git_url'] = package.package.giturl
            if package.package.gitbranch:
                item['branch'] = package.package.gitbranch
            if package.package.upload:
                item['zip_file_number'] = package.package.upload
            packages.append(item)
        return jsonify(packages)
    if request.method == 'DELETE':
        if not current_app.config['ALLOW_UPDATES']:
            return ('File not found', 404)
        target = request.args.get('package', None)
        do_restart = true_or_false(request.args.get('restart', True))
        if target is None:
            return jsonify_with_status("Missing package name.", 400)
        package_list, package_auth = get_package_info()
        the_package = None
        for package in package_list:
            if package.package.name == target:
                the_package = package
                break
        if the_package is None:
            return jsonify_with_status("Package not found.", 400)
        if not the_package.can_uninstall:
            return jsonify_with_status("You are not allowed to uninstall that package.", 400)
        uninstall_package(target)
        if do_restart:
            logmessage("Starting process of updating packages followed by restarting server")
            result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', pargs={'run_create': should_run_create(target)}))
            #result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(target)))
        else:
            result = celery_app.signature('tasks.update_packages', pargs={"restart": False}).delay()
            # result = docassemble.webapp.worker.update_packages.delay(restart=False)
        return jsonify_task(result)
    if request.method == 'POST':
        if not current_app.config['ALLOW_UPDATES']:
            return ('File not found', 404)
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        do_restart = true_or_false(post_data.get('restart', True))
        num_commands = 0
        if 'update' in post_data:
            num_commands += 1
        if 'github_url' in post_data:
            num_commands += 1
        if 'pip' in post_data:
            num_commands += 1
        if 'zip' in request.files:
            num_commands += 1
        if num_commands == 0:
            return jsonify_with_status("No instructions provided.", 400)
        if num_commands > 1:
            return jsonify_with_status("Only one package can be installed or updated at a time.", 400)
        if 'update' in post_data:
            target = post_data['update']
            package_list, package_auth = get_package_info()
            the_package = None
            for package in package_list:
                if package.package.name == target:
                    the_package = package
                    break
            if the_package is None:
                return jsonify_with_status("Package not found.", 400)
            if not the_package.can_update:
                return jsonify_with_status("You are not allowed to update that package.", 400)
            existing_package = db.session.execute(select(Package).filter_by(name=target, active=True).order_by(Package.id.desc())).scalar()
            if existing_package is not None:
                if existing_package.type == 'git' and existing_package.giturl is not None:
                    if existing_package.gitbranch:
                        install_git_package(target, existing_package.giturl, existing_package.gitbranch)
                    else:
                        install_git_package(target, existing_package.giturl, get_master_branch(existing_package.giturl))
                elif existing_package.type == 'pip':
                    if existing_package.name == 'docassemble.webapp' and existing_package.limitation:
                        existing_package.limitation = None
                    install_pip_package(existing_package.name, existing_package.limitation)
            db.session.commit()
            if do_restart:
                logmessage("Starting process of updating packages followed by restarting server")
                result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', pargs={'run_create': should_run_create(target)}))
                #result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(target)))
            else:
                result = celery_app.signature('tasks.update_packages', pargs={"restart": False}).delay()
                # result = docassemble.webapp.worker.update_packages.delay(restart=False)
            return jsonify_task(result)
        if 'github_url' in post_data:
            github_url = post_data['github_url'].rstrip('/')
            branch = post_data.get('branch', None)
            if branch is None:
                branch = get_master_branch(github_url)
            m = re.search(r'#egg=(.*)', github_url)
            if m:
                packagename = re.sub(r'&.*', '', m.group(1))
                github_url = re.sub(r'#.*', '', github_url)
            else:
                packagename = re.sub(r'/*$', '', github_url)
                packagename = re.sub(r'^git+', '', packagename)
                packagename = re.sub(r'#.*', '', packagename)
                packagename = re.sub(r'\.git$', '', packagename)
                packagename = re.sub(r'.*/', '', packagename)
                packagename = re.sub(r'^docassemble-', 'docassemble.', packagename)
            if user_can_edit_package(giturl=github_url) and user_can_edit_package(pkgname=packagename):
                install_git_package(packagename, github_url, branch)
                if do_restart:
                    logmessage("Starting process of updating packages followed by restarting server")
                    result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', pargs={'run_create': should_run_create(packagename)}))
                    # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(packagename)))
                else:
                    result = celery_app.signature('tasks.update_packages', pargs={"restart": False}).delay()
                    # result = docassemble.webapp.worker.update_packages.delay(restart=False)
                return jsonify_task(result)
            jsonify_with_status("You do not have permission to install that package.", 403)
        if 'pip' in post_data:
            m = re.match(r'([^>=<]+)([>=<]+.+)', post_data['pip'])
            if m:
                packagename = m.group(1)
                limitation = m.group(2)
            else:
                packagename = post_data['pip']
                limitation = None
            packagename = re.sub(r'[^A-Za-z0-9\_\-\.]', '', packagename)
            if user_can_edit_package(pkgname=packagename):
                install_pip_package(packagename, limitation)
                if do_restart:
                    logmessage("Starting process of updating packages followed by restarting server")
                    result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', pargs={'run_create': should_run_create(packagename)}))
                    # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(packagename)))
                else:
                    result = celery_app.signature('tasks.update_packages', pargs={"restart": False}).delay()
                    # result = docassemble.webapp.worker.update_packages.delay(restart=False)
                return jsonify_task(result)
            return jsonify_with_status("You do not have permission to install that package.", 403)
        if 'zip' in request.files and request.files['zip'].filename:
            try:
                the_file = request.files['zip']
                filename = secure_filename(the_file.filename)
                file_number = get_new_file_number(get_uid(), filename, None)
                saved_file = SavedFile(file_number, extension='zip', fix=True, should_not_exist=True)
                file_set_attributes(file_number, private=True, persistent=True, session=None, filename=None)
                zippath = saved_file.path
                the_file.save(zippath)
                saved_file.save()
                saved_file.finalize()
                pkgname = get_package_name_from_zip(zippath)
                if user_can_edit_package(pkgname=pkgname):
                    install_zip_package(pkgname, file_number)
                    if do_restart:
                        logmessage("Starting process of updating packages followed by restarting server")
                        result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', pargs={'run_create': should_run_create(pkgname)}))
                        # result = docassemble.webapp.worker.update_packages.apply_async(link=docassemble.webapp.worker.reset_server.s(run_create=should_run_create(pkgname)))
                    else:
                        result = celery_app.signature('tasks.update_packages', pargs={"restart": False}).delay()
                        # result = docassemble.webapp.worker.update_packages.delay(restart=False)
                    return jsonify_task(result)
                return jsonify_with_status("You do not have permission to install that package.", 403)
            except Exception as err:
                return jsonify_with_status(f"There was an error when installing that package. {err.__class__.__name__}: {err}", 400)
    return ('File not found', 404)


@packages_bp.route('/api/package_update_status', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_package_update_status():
    if not current_app.config['ALLOW_UPDATES']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['manage_packages']):
        return jsonify_with_status("Access denied.", 403)
    code = request.args.get('task_id', None)
    if code is None:
        return jsonify_with_status("Missing task_id", 400)
    the_key = 'da:install_status:' + str(code)
    task_data = r.get(the_key)
    if task_data is None:
        return jsonify({'status': 'unknown'})
    task_info = json.loads(task_data.decode())
    result = celery_app.AsyncResult(id=task_info['id'])
    if result.ready():
        the_result = result.get()
        if the_result.__class__.__name__ == 'ReturnValue':
            if the_result.ok:
                if the_result.restart and (START_TIME <= task_info['server_start_time'] or reset_process_running()):
                    return jsonify(status='working')
                r.expire(the_key, 30)
                return jsonify(status='completed', ok=True, log=summarize_results(the_result.results, the_result.logmessages, html=False))
            if hasattr(the_result, 'error_message'):
                r.expire(the_key, 30)
                return jsonify(status='completed', ok=False, error_message=str(the_result.error_message))
            if hasattr(the_result, 'results') and hasattr(the_result, 'logmessages'):
                r.expire(the_key, 30)
                return jsonify(status='completed', ok=False, error_message=summarize_results(the_result.results, the_result.logmessages, html=False))
            r.expire(the_key, 30)
            return jsonify(status='completed', ok=False, error_message=str("No error message.  Result is " + str(the_result)))
        r.expire(the_key, 30)
        return jsonify(status='completed', ok=False, error_message=str(the_result))
    return jsonify(status='working')
