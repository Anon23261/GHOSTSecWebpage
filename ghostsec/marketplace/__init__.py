from flask import Blueprint

marketplace = Blueprint('marketplace', __name__)

from . import routes
