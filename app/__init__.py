# Import flask and template operators
from flask import Flask, render_template, request

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404

# User routes
@app.route('/user', methods=['GET'])
def user():
  return 'GET /user\n'

@app.route('/user/create', methods=['POST'])
def user_create():
  first = request.json['first']
  last  = request.json['last']
  phone = request.json['phone']
  email = request.json['email']
  # Create the user
  return 'POST /user/create\n'

@app.route('/user/update', methods=['POST'])
def user_update():
  return 'POST /user/update\n'

@app.route('/user/delete', methods=['POST'])
def user_delete():
  return 'POST /user/delete\n'

# Car routes
@app.route('/car', methods=['GET'])
def car():
  return 'GET /car\n'

@app.route('/car/create', methods=['POST'])
def car_create():
  return 'POST /car/create\n'

@app.route('/car/update', methods=['POST'])
def car_update():
  return 'POST /car/update\n'

@app.route('/car/delete', methods=['POST'])
def car_delete():
  return 'POST /car/delete\n'

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_auth.controllers import mod_auth as auth_module

# Register blueprint(s)
app.register_blueprint(auth_module)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
