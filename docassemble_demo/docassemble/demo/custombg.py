# do not pre-load
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.tasks.context import bg_context
from docassemble.base.util import comma_and_list

@celery_app.task
def custom_add_four(operand):
    return operand + 4


@celery_app.task
def custom_comma_and_list(*pargs):
    with bg_context():
        return comma_and_list(*pargs)
