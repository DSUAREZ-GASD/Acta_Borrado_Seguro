from flask import Blueprint

pdf =  Blueprint('pdf',
                 __name__,
                 url_prefix='/pdf',
                 static_folder='static')


from . import routes
