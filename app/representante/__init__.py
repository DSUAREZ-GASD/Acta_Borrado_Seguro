from flask import Blueprint

representantes = Blueprint(
    "representante",
    __name__,
    url_prefix="/representantes",
    template_folder="templates",
    static_folder="static",
)

from . import routes
