# pylint: disable=wrong-import-position
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load()
from contextlib import ExitStack
from docassemble.base.thread_context import this_thread, global_context, user_dict_context, empty_globals
from docassemble.webapp.config import daconfig
from docassemble.webapp.interview.dictionary import fresh_dictionary
from docassemble.webapp.users.helpers import login_as_admin
from docassemble.webapp.flask_app import flaskapp as app

class TestContext:

    def __init__(self, package):
        self.package = package
        self.stack = ExitStack()

    def __enter__(self):
        url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
        url = url_root + 'interview'
        self.app_context = self.stack.enter_context(app.app_context())
        self.test_context = self.stack.enter_context(app.test_request_context(base_url=url_root, path=url))
        app.preprocess_request()
        login_as_admin(url, url_root)
        self.stack.enter_context(global_context(empty_globals()))
        self.stack.enter_context(user_dict_context(fresh_dictionary()))
        this_thread.current_package = self.package
        this_thread.current_info.update({'yaml_filename': self.package + ':data/questions/test.yml'})
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        app.login_manager._update_request_context_with_user()  # pylint: disable=no-member
        self.stack.close()
