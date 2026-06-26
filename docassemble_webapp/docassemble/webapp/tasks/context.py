from contextlib import contextmanager
from docassemble.webapp.config import daconfig
from docassemble.webapp.utils.helpers import set_request_active
from docassemble.webapp.flask_app import flaskapp

@contextmanager
def bg_context():
    # worker_controller.initialize()
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    with flaskapp.app_context() as a, flaskapp.test_request_context(base_url=url_root, path=url) as b:
        flaskapp.preprocess_request()
        # worker_controller.functions.reset_local_variables()
        set_request_active(False)
        yield (a, b)
