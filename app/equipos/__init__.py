from flask import Blueprint

equipos = Blueprint('equipos',
                        __name__,
                        url_prefix= '/equipos',
                        template_folder='templates',
                        static_folder='imagenes')

from . import routes
