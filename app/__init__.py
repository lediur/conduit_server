# Import flask and template operators
from flask import Flask, render_template, request, jsonify

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404

# User routes
@app.route('/user', methods=['GET'])
def user():
  users = [{
    'first': user.first,
    'last': user.last,
    'phone': user.phone,
    'email': user.email
  } for user in User.query.all()]
  return jsonify(users=users)

@app.route('/user/create', methods=['POST'])
def user_create():
  first = request.json['first']
  last  = request.json['last']
  phone = request.json['phone']
  email = request.json['email']

  # Create the user
  u = User(first, last, phone, email)
  db.add(u)
  db.commit()
  
  user = {
    'first': u.first,
    'last': u.last,
    'phone': u.phone,
    'email': u.email
  }

  return jsonify(user=user)

@app.route('/user/update', methods=['POST'])
def user_update():
  return 'POST /user/update\n'

@app.route('/user/delete', methods=['POST'])
def user_delete():
  User.query.delete()  
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


from app.database import db

@app.teardown_appcontext
def shutdown_session(exception=None):
  db.remove()

from app.database import init_db
init_db()

from app.database import db
from app.models import User