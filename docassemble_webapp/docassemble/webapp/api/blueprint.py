from flask import Blueprint

api_bp = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)
