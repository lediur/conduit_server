# Import flask and template operators
from flask import abort, Flask, render_template, request, jsonify

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

import routes as Routes

from app.database import db, init_db
init_db()

@app.errorhandler(404)
def not_found(error):
  abort(404)

@app.teardown_appcontext
def shutdown_session(exception=None):
  db.remove()
