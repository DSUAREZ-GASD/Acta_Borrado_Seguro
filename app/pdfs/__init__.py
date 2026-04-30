from flask import Blueprint

pdf =  Blueprint('pdf',
                 __name__,
                 url_prefix='/pdf',
                 static_folder='static',
                 template_folder='templates')


from . import routes
