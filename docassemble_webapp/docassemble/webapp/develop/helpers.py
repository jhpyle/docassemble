import json
import stat
import sys
import os
import re
import shutil
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import YamlLexer  # pylint: disable=no-name-in-module
import oauth2client
from Crypto.PublicKey import RSA
from markupsafe import Markup
from sqlalchemy import select, or_, and_
from flask import current_app, session
from flask_login import current_user
from docassemble.base.error import DAError
from docassemble.base.functions import safeyaml
from docassemble.base.language.words import word
from docassemble.base.logger import logmessage
from docassemble.webapp.cloud.utils import cloud
from docassemble.webapp.config import (
    daconfig,
    UPLOAD_DIRECTORY,
    FULL_PACKAGE_DIRECTORY,
    WEBAPP_PATH,
    LOG_DIRECTORY,
    da_version,
    hostname,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.files.file_access import get_info_from_file_reference
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.users.models import UserRoles, UserModel, Role
from docassemble.webapp.utils.helpers import (
    fix_tabs,
    fix_initial,
    document_match,
    make_example_html,
    safeid,
    get_base_words,
)
from docassemble.webapp.utils.hooks import url_for

pg_ex = {}
base_words = {}

def copy_playground_modules():
    progress_key = 'da:copying_playground_modules:' + hostname
    in_progress = r.get(progress_key)
    if in_progress is not None:
        return
    pipe = r.pipeline()
    pipe.set(progress_key, 1)
    pipe.expire(progress_key, 5)
    pipe.execute()
    root_dir = os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble')
    for d in os.listdir(root_dir):
        if re.search(r'^playground[0-9]', d) and os.path.isdir(os.path.join(root_dir, d)):
            try:
                shutil.rmtree(os.path.join(root_dir, d))
            except:
                logmessage("copy_playground_modules: error deleting " + os.path.join(root_dir, d))
    devs = set()
    for user in db.session.execute(select(UserModel.id).join(UserRoles, UserModel.id == UserRoles.user_id).join(Role, UserRoles.role_id == Role.id).where(and_(UserModel.active == True, or_(Role.name == 'admin', Role.name == 'developer')))):  # noqa: E712 # pylint: disable=singleton-comparison
        devs.add(user.id)
    for user_id in devs:
        mod_dir = SavedFile(user_id, fix=True, section='playgroundmodules')
        local_dirs = [(os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'playground' + str(user_id)), mod_dir.directory)]
        for dirname in mod_dir.list_of_dirs():
            local_dirs.append((os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'playground' + str(user_id) + dirname), os.path.join(mod_dir.directory, dirname)))
        for local_dir, mod_directory in local_dirs:
            if os.path.isdir(local_dir):
                try:
                    shutil.rmtree(local_dir)
                except:
                    logmessage("copy_playground_modules: error deleting " + local_dir + " before replacing it")
            os.makedirs(local_dir, exist_ok=True)
            # logmessage("Copying " + str(mod_directory) + " to " + str(local_dir))
            for f in [f for f in os.listdir(mod_directory) if re.search(r'^[A-Za-z].*\.py$', f)]:
                shutil.copyfile(os.path.join(mod_directory, f), os.path.join(local_dir, f))
            # shutil.copytree(mod_dir.directory, local_dir)
            # with open(os.path.join(local_dir, '__init__.py'), 'w', encoding='utf-8') as the_file:
            #     the_file.write(init_py_file)
    pipe = r.pipeline()
    pipe.set(progress_key, 1)
    pipe.expire(progress_key, 3)
    pipe.execute()


def proc_example_list(example_list, package, directory, examples):
    for example in example_list:
        if isinstance(example, dict):
            for key, value in example.items():
                sublist = []
                proc_example_list(value, package, directory, sublist)
                examples.append({'title': str(key), 'list': sublist})
                break
            continue
        result = {}
        result['id'] = example
        result['interview'] = url_for('interview.index', reset=1, i=package + ":data/questions/" + directory + example + ".yml")
        example_file = package + ":data/questions/" + directory + example + '.yml'
        if package == 'docassemble.base':
            result['image'] = url_for('static', filename=directory + example + ".png", v=da_version)
        else:
            result['image'] = url_for('main.package_static', package=package, filename=example + ".png")
        # logmessage("Giving it " + example_file)
        file_info = get_info_from_file_reference(example_file)
        # logmessage("Got back " + file_info['fullpath'])
        start_block = 1
        end_block = 2
        if 'fullpath' not in file_info or file_info['fullpath'] is None:
            logmessage("proc_example_list: could not find " + example_file)
            continue
        with open(file_info['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            content = fix_initial.sub('', content)
            blocks = list(map(lambda x: x.strip(), document_match.split(content)))
            if len(blocks) > 0:
                has_context = False
                for block in blocks:
                    if re.search(r'metadata:', block):
                        try:
                            the_block = safeyaml.load(block)
                            if isinstance(the_block, dict) and 'metadata' in the_block:
                                the_metadata = the_block['metadata']
                                result['title'] = the_metadata.get('title', the_metadata.get('short title', word('Untitled')))
                                if isinstance(result['title'], dict):
                                    result['title'] = result['title'].get('en', word('Untitled'))
                                result['title'] = result['title'].rstrip()
                                result['documentation'] = the_metadata.get('documentation', None)
                                start_block = int(the_metadata.get('example start', 1))
                                end_block = int(the_metadata.get('example end', start_block)) + 1
                                break
                        except BaseException as err:
                            logmessage("proc_example_list: error processing " + example_file + ": " + str(err))
                            continue
                if 'title' not in result:
                    logmessage("proc_example_list: no title in " + example_file)
                    continue
                if re.search(r'metadata:', blocks[0]) and start_block > 0:
                    initial_block = 1
                else:
                    initial_block = 0
                if start_block > initial_block:
                    result['before_html'] = highlight("\n---\n".join(blocks[initial_block:start_block]) + "\n---", YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight'))
                    has_context = True
                else:
                    result['before_html'] = ''
                if len(blocks) > end_block:
                    result['after_html'] = highlight("---\n" + "\n---\n".join(blocks[end_block:len(blocks)]), YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight'))
                    has_context = True
                else:
                    result['after_html'] = ''
                result['source'] = "\n---\n".join(blocks[start_block:end_block])
                result['html'] = highlight(result['source'], YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight'))
                result['has_context'] = has_context
            else:
                logmessage("proc_example_list: no blocks in " + example_file)
                continue
        examples.append(result)


def get_examples():
    examples = []
    file_list = daconfig.get('playground examples', ['docassemble.base:data/questions/example-list.yml'])
    if not isinstance(file_list, list):
        file_list = [file_list]
    for the_file in file_list:
        if not isinstance(the_file, str):
            continue
        example_list_file = get_info_from_file_reference(the_file)
        the_package = ''
        if 'fullpath' in example_list_file and example_list_file['fullpath'] is not None:
            if 'package' in example_list_file:
                the_package = example_list_file['package']
            else:
                continue
            if the_package == 'docassemble.base':
                the_directory = 'examples/'
            else:
                the_directory = ''
            if os.path.exists(example_list_file['fullpath']):
                try:
                    with open(example_list_file['fullpath'], 'r', encoding='utf-8') as fp:
                        content = fp.read()
                        content = fix_tabs.sub('  ', content)
                        proc_example_list(safeyaml.load(content), the_package, the_directory, examples)
                except BaseException as the_err:
                    logmessage("There was an error loading the Playground examples:" + str(the_err))
    # logmessage("Examples: " + str(examples))
    return examples


def add_project(filename, current_project):
    if current_project == 'default':
        return filename
    return os.path.join(current_project, filename)


def write_pypirc():
    progress_key = 'da:writing_pypirc:' + hostname
    in_progress = r.get(progress_key)
    if in_progress is not None:
        return
    pipe = r.pipeline()
    pipe.set(progress_key, 1)
    pipe.expire(progress_key, 5)
    pipe.execute()
    pypirc_file = daconfig.get('pypirc path', '/var/www/.pypirc')
    # pypi_username = daconfig.get('pypi username', None)
    # pypi_password = daconfig.get('pypi password', None)
    pypi_url = daconfig.get('pypi url', 'https://upload.pypi.org/legacy/')
    # if pypi_username is None or pypi_password is None:
    #     return
    if os.path.isfile(pypirc_file):
        with open(pypirc_file, 'r', encoding='utf-8') as fp:
            existing_content = fp.read()
    else:
        existing_content = None
    content = """\
[distutils]
index-servers =
  pypi

[pypi]
repository: """ + pypi_url + "\n"
#     """
# username: """ + pypi_username + """
# password: """ + pypi_password + "\n"
    if existing_content != content:
        with open(pypirc_file, 'w', encoding='utf-8') as fp:
            fp.write(content)
        os.chmod(pypirc_file, stat.S_IRUSR | stat.S_IWUSR)
    pipe = r.pipeline()
    pipe.set(progress_key, 1)
    pipe.expire(progress_key, 3)
    pipe.execute()


def get_github_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('github', {})
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('GitHub integration is not configured')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='repo admin:public_key read:user user:email read:org',
        redirect_uri=url_for('develop.github_oauth_callback', _external=True),
        auth_uri='https://github.com/login/oauth/authorize',
        token_uri='https://github.com/login/oauth/access_token',
        access_type='offline',
        prompt='consent')
    return flow


def delete_ssh_keys():
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    area.delete_file('.ssh-private')
    area.delete_file('.ssh-public')
    # area.delete_file('.ssh_command.sh')
    area.finalize()


def get_ssh_keys(email):
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    private_key_file = os.path.join(area.directory, '.ssh-private')
    public_key_file = os.path.join(area.directory, '.ssh-public')
    if (not (os.path.isfile(private_key_file) and os.path.isfile(private_key_file))) or (not (os.path.isfile(public_key_file) and os.path.isfile(public_key_file))):
        key = RSA.generate(4096)
        pubkey = key.publickey()
        area.write_content(key.exportKey('PEM').decode(), filename=private_key_file, save=False)
        pubkey_text = pubkey.exportKey('OpenSSH').decode() + " " + str(email) + "\n"
        area.write_content(pubkey_text, filename=public_key_file, save=False)
        area.finalize()
    return (private_key_file, public_key_file)


def make_necessary_dirs():
    paths = []
    if current_app.config['ALLOW_UPDATES'] or current_app.config['ENABLE_PLAYGROUND']:
        paths.append(FULL_PACKAGE_DIRECTORY)
    if cloud is None:
        paths.append(UPLOAD_DIRECTORY)
    paths.append(LOG_DIRECTORY)
    for path in paths:
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except:
                sys.exit("Could not create path: " + path)
        if not os.access(path, os.W_OK):
            sys.exit("Unable to create files in directory: " + path)
    if current_app.config['ALLOW_RESTARTING'] and not os.access(WEBAPP_PATH, os.W_OK):
        sys.exit("Unable to modify the timestamp of the WSGI file: " + WEBAPP_PATH)


def define_examples():
    if 'encoded_example_html' in pg_ex:
        return
    example_html = []
    example_html.append('        <div class="col-md-2">\n          <h5 class="mb-1">Example blocks</h5>')
    pg_ex['pg_first_id'] = []
    data_dict = {}
    make_example_html(get_examples(), pg_ex['pg_first_id'], example_html, data_dict)
    if len(data_dict) == 0:
        pg_ex['encoded_data_dict'] = None
        pg_ex['encoded_example_html'] = ""
        return
    example_html.append('        </div>')
    example_html.append('        <div class="col-md-4 da-example-source-col"><h5 class="mb-1">' + word('Source') + '<a href="#" tabindex="0" class="dabadge btn btn-success da-example-copy">' + word("Insert") + '</a></h5><div id="da-example-source-before" class="dainvisible"></div><div id="da-example-source"></div><div id="da-example-source-after" class="dainvisible"></div><div><a tabindex="0" class="da-example-hider" id="da-show-full-example">' + word("Show context of example") + '</a><a tabindex="0" class="da-example-hider dainvisible" id="da-hide-full-example">' + word("Hide context of example") + '</a></div></div>')
    example_html.append('        <div class="col-md-6"><h5 class="mb-1">' + word("Preview") + '<a href="#" target="_blank" class="dabadge btn btn-primary da-example-documentation da-example-hidden" id="da-example-documentation-link">' + word("View documentation") + '</a></h5><a href="#" target="_blank" id="da-example-image-link"><picture><source media="(prefers-color-scheme: dark)" id="da-example-image-dark" /><img title=' + json.dumps(word("Click to try this interview")) + ' class="da-example-screenshot" id="da-example-image" /></picture></a></div>')
    pg_ex['encoded_data_dict'] = safeid(json.dumps(data_dict))
    pg_ex['encoded_example_html'] = Markup("\n".join(example_html))


def set_playground_user(user_id):
    if user_id == current_user.id:
        if 'playground_user' in session:
            del session['playground_user']
    else:
        session['playground_user'] = user_id


def compute_base_words():
    base_words.clear()
    base_words.update(get_base_words())
