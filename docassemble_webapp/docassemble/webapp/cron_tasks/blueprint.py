from flask import Blueprint

cron_bp = Blueprint(
    'cron_cli',
    __name__,
    cli_group='cron'
)
