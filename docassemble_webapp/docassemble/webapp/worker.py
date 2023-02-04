import importlib
from celery import Celery, chord  # noqa: F401 # pylint: disable=unused-import
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig
from docassemble.base.logger import logmessage
from docassemble.webapp.worker_common import workerapp, convert, bg_context  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.worker_tasks import background_action, ocr_page, ocr_google, make_png_for_pdf, email_attachments, update_packages, sync_with_google_drive, sync_with_onedrive, ocr_dummy, ocr_finalize, reset_server  # noqa: F401 # pylint: disable=unused-import

for module_name in daconfig['celery modules']:
    try:
        importlib.import_module(module_name)
    except:
        logmessage("Error importing " + module_name + " from celery modules list")
