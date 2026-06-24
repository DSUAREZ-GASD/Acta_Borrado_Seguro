from flask import Blueprint

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')

from app.dashboard import routes