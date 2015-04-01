from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, User

from app.utils import user_param_keys, validate

# User routes
@app.route('/users', methods=['GET'])
def get_users():
  response = []
  users = []

  if ('car_id' in request.args):
    car_id = request.args['car_id']
    users = Car.query.get(car_id).users
  else:
    users = User.query.all()

  for user in users:
    user_props = {}
    for param_key in user_param_keys:
      user_props[param_key] = user.get(param_key)
    user_props['id'] = user.id
    response.append(user_props)
  return jsonify(users=response)

@app.route('/users/<user_id>', methods=['GET'])
def get_users_by_user_id(user_id):
  response = {}
  
  user_id = int(user_id)
  user = User.query.get(user_id)
  if (not user):
    return 'Cannot find user_id %d\n' % user_id, 400

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users/create', methods=['POST'])
def create_user():
  omitted = []
  invalid = []
  response = {}

  for param_key in user_param_keys:
    if (param_key not in request.json):
      omitted.append(param_key)

  if (len(omitted) > 0):
    return 'Must provide %s\n' % ', '.join(omitted), 400

  for param_key in user_param_keys:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400
  
  email_address = request.json['email_address']
  first_name = request.json['first_name']
  last_name  = request.json['last_name']
  phone_number = request.json['phone_number']
  push_enabled = request.json['push_enabled']

  user = User(email_address, first_name, last_name, phone_number, push_enabled)
  if (not user):
    return 'Failed to create user\n', 400
  db.add(user)
  db.commit()
  
  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users/update/<user_id>', methods=['POST'])
def update_user(user_id):
  present = []
  invalid = []
  response = {}

  for param_key in user_param_keys:
    if (param_key in request.json):
      present.append(param_key)

  if (len(present) == 0):
    return 'Must provide at least one parameter\n', 400

  for param_key in present:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  user_id = int(user_id)
  user = User.query.get(user_id)
  if (not user):
    return 'Cannot find user_id %d\n' % user_id, 400

  for param_key in present:
    user.set(param_key, request.json[param_key])

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
  user_id = int(user_id)
  user = User.query.get(user_id)
  if (not user):
    return 'Cannot find user_id %d\n' % user_id, 400
  User.query.filter_by(id=user_id).delete()
  return '', 200
