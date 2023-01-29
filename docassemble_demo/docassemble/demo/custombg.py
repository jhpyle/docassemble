# do not pre-load
from docassemble.webapp.worker_common import workerapp, bg_context, worker_controller as wc


@workerapp.task
def custom_add_four(operand):
    return operand + 4


@workerapp.task
def custom_comma_and_list(*pargs):
    with bg_context():
        return wc.util.comma_and_list(*pargs)
