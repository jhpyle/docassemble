from flask import Blueprint

monitor_bp = Blueprint(
    'monitor',
    __name__,
    template_folder='templates'
)
