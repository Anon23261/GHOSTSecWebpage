from flask import Blueprint

oauth = Blueprint('oauth', __name__)

from . import routes
