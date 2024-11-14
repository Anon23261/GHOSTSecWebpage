from flask import Blueprint

learning = Blueprint('learning', __name__)

from . import routes
