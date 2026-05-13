from flask import Blueprint

usuarios = Blueprint(
    "usuario", __name__, url_prefix="/usuarios", template_folder="templates"
)
from . import routes
