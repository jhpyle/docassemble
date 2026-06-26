import os
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.control import set_language, set_locale, update_locale
from docassemble.webapp.config import (
    daconfig,
    hostname,
    DEFER,
    DEFAULT_LANGUAGE,
    DEFAULT_DIALECT,
    DEFAULT_VOICE,
    DEFAULT_LOCALE,
)
from docassemble.webapp.develop.helpers import (
    copy_playground_modules,
    write_pypirc,
    make_necessary_dirs,
    compute_base_words,
)
from docassemble.webapp.flask_app import flaskapp as app
from docassemble.webapp.interview.config import page_parts
from docassemble.webapp.lock import release_lock, obtain_lock
from docassemble.webapp.mail.helpers import compute_mail_config
from docassemble.webapp.main.helpers import set_admin_interviews, test_favicon_file
from docassemble.webapp.packages.helpers import import_necessary
from docassemble.webapp.testing import TestContext  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.utils.helpers import (
    fix_words,
    get_url_from_file_reference,
    populate_dicts,
)
from docassemble.webapp.utils.logger import logmessage

# password_secret_key = daconfig.get('password secretkey', app.secret_key)

def initialize():
    global_css = ''
    global_js = ''
    with app.app_context():
        make_necessary_dirs()
        url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
        url = url_root + 'interview'
        with app.test_request_context(base_url=url_root, path=url):
            app.preprocess_request()
            set_language(DEFAULT_LANGUAGE, dialect=DEFAULT_DIALECT, voice=DEFAULT_VOICE)
            set_locale(DEFAULT_LOCALE)
            update_locale()
            fix_words()
            populate_dicts()
            compute_base_words()
            compute_mail_config()
            if app.config['ENABLE_FAX']:
                from docassemble.webapp.fax.helpers import populate_fax_config
                populate_fax_config()
            app.config['USE_FAVICON'] = test_favicon_file('favicon.ico')
            app.config['USE_APPLE_TOUCH_ICON'] = test_favicon_file('apple-touch-icon.png')
            app.config['USE_FAVICON_MD'] = test_favicon_file('favicon-32x32.png')
            app.config['USE_FAVICON_SM'] = test_favicon_file('favicon-16x16.png')
            app.config['USE_SITE_WEBMANIFEST'] = test_favicon_file('site.webmanifest', alt='manifest.json')
            app.config['USE_SAFARI_PINNED_TAB'] = test_favicon_file('safari-pinned-tab.svg')
            if 'bootstrap theme' in daconfig and daconfig['bootstrap theme']:
                try:
                    app.config['BOOTSTRAP_THEME'] = get_url_from_file_reference(daconfig['bootstrap theme'], {})
                    assert isinstance(app.config['BOOTSTRAP_THEME'], str)
                except:
                    app.config['BOOTSTRAP_THEME'] = None
                    logmessage("error loading bootstrap theme")
            else:
                app.config['BOOTSTRAP_THEME'] = None
            if 'global css' in daconfig:
                for fileref in daconfig['global css']:
                    try:
                        global_css_url = get_url_from_file_reference(fileref, {})
                        assert isinstance(global_css_url, str)
                        global_css += "\n" + '    <link href="' + global_css_url + '" rel="stylesheet">'
                    except:
                        logmessage("error loading global css: " + repr(fileref))
            if 'global javascript' in daconfig:
                for fileref in daconfig['global javascript']:
                    try:
                        global_js_url = get_url_from_file_reference(fileref, {})
                        assert isinstance(global_js_url, str)
                        global_js += "\n" + f'    <script{DEFER} src="{global_js_url}"></script>'
                    except:
                        logmessage("error loading global js: " + repr(fileref))
            if 'raw global css' in daconfig and daconfig['raw global css']:
                global_css += "\n" + str(daconfig['raw global css'])
            if 'raw global javascript' in daconfig and daconfig['raw global javascript']:
                global_js += "\n" + str(daconfig['raw global javascript'])
            app.config['GLOBAL_CSS'] = global_css
            app.config['GLOBAL_JS'] = global_js
            app.config['PARTS'] = page_parts
            app.config['ADMIN_INTERVIEWS'] = set_admin_interviews()
            try:
                if 'image' in daconfig['social'] and isinstance(daconfig['social']['image'], str):
                    daconfig['social']['image'] = get_url_from_file_reference(daconfig['social']['image'], {"_external": True})
                    if daconfig['social']['image'] is None:
                        del daconfig['social']['image']
                for key, subkey in (('og', 'image'), ('twitter', 'image')):
                    if key in daconfig['social'] and isinstance(daconfig['social'][key], dict) and subkey in daconfig['social'][key] and isinstance(daconfig['social'][key][subkey], str):
                        daconfig['social'][key][subkey] = get_url_from_file_reference(daconfig['social'][key][subkey], {"_external": True})
                        if daconfig['social'][key][subkey] is None:
                            del daconfig['social'][key][subkey]
            except:
                logmessage("Error converting social image references")
            interviews_to_load = daconfig.get('preloaded interviews', None)
            if isinstance(interviews_to_load, list):
                for yaml_filename in daconfig['preloaded interviews']:
                    try:
                        get_interview(yaml_filename)
                    except:
                        pass
            if app.config['ENABLE_PLAYGROUND']:
                obtain_lock('init' + hostname, 'init')
                try:
                    copy_playground_modules()
                except BaseException as err:
                    logmessage("There was an error copying the playground modules: " + err.__class__.__name__)
                write_pypirc()
                release_lock('init' + hostname, 'init')
            try:
                macro_path = daconfig.get('libreoffice macro file', '/var/www/.config/libreoffice/4/user/basic/Standard/Module1.xba')
                if os.path.isfile(macro_path) and os.path.getsize(macro_path) != 7167:
                    # logmessage("Removing " + macro_path + " because it is out of date")
                    os.remove(macro_path)
                # else:
                #     logmessage("File " + macro_path + " is missing or has the correct size")
            except BaseException as err:
                logmessage("Error was " + err.__class__.__name__ + ' ' + str(err))
            if app.config['ENABLE_API']:
                from docassemble.webapp.api.helpers import fix_api_keys
                fix_api_keys()
            import_necessary(url, url_root)

application = app
initialize()

if __name__ == "__main__":
    app.run()
