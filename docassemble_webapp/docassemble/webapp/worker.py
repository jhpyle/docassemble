# ruff: noqa: F401
# pylint: disable=wrong-import-position, disable=unused-import
import importlib
from celery import Celery, chord  # noqa: F401 # pylint: disable=unused-import
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.webapp.config import daconfig
from docassemble.webapp.flask_app import flaskapp
from docassemble.webapp.startup import initialize
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.tasks.context import bg_context
from docassemble.webapp.tasks.common import celery_app, convert
from docassemble.webapp.tasks.tasks import (
    background_action,
    email_attachments,
    make_png_for_pdf,
    ocr_dummy,
    ocr_finalize,
    ocr_google,
    ocr_page,
    reset_server,
    sync_with_google_drive,
    sync_with_onedrive,
    update_packages,
)

initialize(flaskapp)

for module_name in daconfig['celery modules']:
    try:
        importlib.import_module(module_name)
    except:
        logmessage("Error importing " + module_name + " from celery modules list")
