from flask import Blueprint

ctf = Blueprint('ctf', __name__)

from . import routes
