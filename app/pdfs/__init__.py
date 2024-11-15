from flask import Blueprint

pdf =  Blueprint('pdf', __name__,
                 url_prefix='/pdf',
                 template_folder='templates',
                 static_folder='static')

from . import routes
