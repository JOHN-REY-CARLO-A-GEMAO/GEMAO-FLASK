from flask import Blueprint

# Templates are served from the project's top-level `templates/` directory.
cashier_bp = Blueprint('cashier', __name__, url_prefix='/cashier')

from . import routes
