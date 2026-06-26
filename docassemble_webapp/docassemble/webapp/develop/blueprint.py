from flask import Blueprint

develop_bp = Blueprint(
    'develop',
    __name__,
    template_folder='templates'
)
