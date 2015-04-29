from flask import jsonify, request, session
from app import app
from app.database import db

from app.models import Car, Session, User

from app.utils import user_param_keys, validate
import Crypto
import jwt
from Crypto.PublicKey import RSA
import os
from datetime import *

# User routes for Production
@app.route('/users/create', methods=['POST'])
def create_user():
  '''
  If the request includes the user_param_keys as body parameters, returns
  the created user. Otherwise, returns 400 Bad Request Error.
  '''
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
  password = request.json['password']
  phone_number = request.json['phone_number']
  push_enabled = request.json['push_enabled']

  user = User(email_address, first_name, last_name, password, phone_number, push_enabled)
  if (not user):
    return 'Failed to create user\n', 400
  db.add(user)
  db.commit()
  
  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)

  return jsonify(response)

@app.route('/users/identifier', methods=['POST'])
def create_identity_token():
  email_address = request.json['email_address']
  # Grab nonce from request
  nonce = request.json['nonce']

  user = User.query.filter_by(email_address=email_address).first()

  priv_rsakey = None
  # Read RSA key
  root = os.path.dirname(__file__)
  with open(os.path.join(root, '../..', 'layer.pem'), 'r') as rsa_priv_file:
    priv_rsakey = rsa_priv_file.read()

  print priv_rsakey
  # Create identity token
  # Make sure you have PyJWT and PyCrypto libraries installed and imported
  identityToken = jwt.encode(
    payload={
      'iss': '7b29a59c-db1b-11e4-b670-52bb02000413',  # The Layer Provider ID
      'prn': email_address,                             # String - Provider's internal ID for the authenticating user
      'iat': datetime.now(),                          # Integer - Time of Token Issuance in RFC 3339 seconds
      'exp': datetime.utcnow() + timedelta(seconds=30),   # Integer - Arbitrary time of Token Expiration in RFC 3339 seconds
      'nce': nonce                                    # The nonce obtained via the Layer client SDK.
    },
    key=priv_rsakey,
    algorithm='RS256',
    headers = {
      'typ': 'JWS',               # String - Expresses a MIME Type of application/JWS
      "alg": "RS256",             # String - Expresses the type of algorithm used to sign the token, must be RS256
      'cty': 'layer-eit;v=1',     # String - Express a Content Type of Layer External Identity Token, version 1
      'kid': '4d3def30-dc83-11e4-852c-52bb25003d93' # Sting - Layer Key ID used to sign the token
    }
  )
  
  print identityToken

  response = {}
  user.set("participant_identifier", identityToken)
  response["participant_identifier"] = identityToken

  return jsonify(response)

# User routes for Development
@app.route('/users', methods=['GET'])
def get_users():
  '''
  If the request includes 'car_id' or 'license_plate' as a query string 
  parameter, returns all owners of the car. Otherwise, returns all users.
  '''
  response = []
  users = []

  if ('car_id' in request.args):
    car_id = request.args['car_id']
    users = Car.query.get(car_id).users
  elif ('license_plate' in request.args):
    license_plate = request.args['license_plate']
    # todo: this doesn't work because there is only one user associated with a car?
    users = Car.query.filter_by(license_plate=license_plate).first().users
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
  '''
  If the request includes 'user_id' as route string parameter, returns the
  corresponding user. Otherwise, returns 400 Bad Request Error.
  '''
  response = {}
  
  user_id = int(user_id)
  user = User.query.get(user_id)
  if (not user):
    return 'Cannot find user_id %d\n' % user_id, 400

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users/<user_id>/update', methods=['POST'])
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

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
  user_id = int(user_id)
  user = User.query.get(user_id)
  if (not user):
    return 'Cannot find user_id %d\n' % user_id, 400
  User.query.filter_by(id=user_id).delete()
  return '', 200