from flask import Blueprint

representantes = Blueprint('representantes', 
                   __name__, 
                   url_prefix= '/representantes', 
                   template_folder='templates',
                   static_folder='static')

from . import routes
