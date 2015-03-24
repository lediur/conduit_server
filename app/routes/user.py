from flask import jsonify, request
from app import app
from app.database import db

from app.models import User

# User routes
@app.route('/users', methods=['GET'])
def user():
  users = [{
    'id': user.id,
    'first': user.first,
    'last': user.last,
    'phone': user.phone,
    'email': user.email
  } for user in User.query.all()]
  
  return jsonify(users=users)

@app.route('/users/create', methods=['POST'])
def user_create():
  first = request.json['first']
  last  = request.json['last']
  phone = request.json['phone']
  email = request.json['email']

  # Create the user
  u = User(email, first, last, phone)
  db.add(u)
  db.commit()
  
  user = {
    'id': u.id,
    'first': u.first,
    'last': u.last,
    'phone': u.phone,
    'email': u.email
  }

  return jsonify(user=user)

@app.route('/users/update', methods=['POST'])
def user_update():
  return 'POST /user/update\n'

@app.route('/users/delete', methods=['POST'])
def user_delete():
  return 'POST /user/delete\n'
