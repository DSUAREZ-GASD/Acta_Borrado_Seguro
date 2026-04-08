from flask import Blueprint

acta_verificacion = Blueprint('acta_verificacion', 
                   __name__, 
                   url_prefix= '/acta_verificacion', 
                   template_folder='templates',
                   static_folder='static')

from . import routes