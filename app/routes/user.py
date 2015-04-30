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

#==============================================================================
# Get, Create, Update, Delete users
#==============================================================================
@app.route('/users/<session_token>', methods=['GET'])
def get_user(session_token):
  '''
  Route for GET /users/<session_token>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
  Returns:
    If validation succeeds -- user associated with the session identifier
      @session_token
    If validation fails -- description of failure
  '''
  response = {}

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  # Retrieves user
  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users', methods=['POST'])
def create_user():
  '''
  Route for POST /users
  Accepts:
    @email_address -- email address passed in the body of the request
    @first_name -- first name passed in the body of the request
    @last_name -- last name passed in the body of the request
    @password -- passwords passed in the body of the request
    @phone_number -- phone number passed in the body of the request
    @push_enabled -- push enabled passed in the body of the request
  Description:
    Creates a new user with email address @email_address, first name
    @first_name, last name @last_name, password @password, phone number
    @phone_number, and push enabled @push_enabled.
  Returns:
    If validation succeeds -- created user
    If validation fails -- description of failure
  '''
  omitted = []
  invalid = []
  response = {}

  # Validates user information
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

  user = User.query.filter_by(email_address=email_address).first()
  if (user):
    # If user exists, do not create user
    return 'Failed to create user\n', 400
  user = User(email_address, first_name, last_name, password, phone_number, push_enabled)
  if (not user):
    return 'Failed to create user\n', 400
  db.add(user)
  db.commit()

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)

  return jsonify(response)

@app.route('/users/<session_token>', methods=['PUT'])
def update_user(session_token):
  '''
  Route for PUT /users/<session_token>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @email_address -- optional email address passed in the body of the request
    @first_name -- optional first name passed in the body of the request
    @last_name -- optional last name passed in the body of the request
    @password -- optional passwords passed in the body of the request
    @phone_number -- optional phone number passed in the body of the request
    @push_enabled -- optional push enabled passed in the body of the request
  Description:
    Updates an existing user with email address @email_address, first name
    @first_name, last name @last_name, password @password, phone number
    @phone_number, or push enabled @push_enabled.
  Returns:
    If validation succeeds -- updates user
    If validation fails -- description of failure
  '''
  present = []
  invalid = []
  response = {}

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  # Validates updated user information
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

  # Updates user
  for param_key in present:
    user.set(param_key, request.json[param_key])

  # Retrieves user
  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/users/<session_token>', methods=['DELETE'])
def delete_user(session_token):
  '''
  Route for DELETE /users/<session_token>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
  Description:
    Deletes an existing user with the session identifier @session_token.
  Returns:
    If validation succeeds -- description of success
    If validation fails -- description of failure
  '''
  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  User.query.filter_by(id=user_id).delete()
  return '', 200

#==============================================================================
# Get, Update, Create, Delete cars associated with user
#==============================================================================
@app.route('/users/<session_token>/cars', methods=['GET'])
def get_cars(session_token):
  '''
  Route for GET /users/<session_token>/cars
  Accepts:
    @session_token -- valid identifier passed in the route of the request
  Returns:
    If validation succeeds -- list of cars owned by the user associated with
      the session identifier @session_token.
    If validation fails -- description of failure
  '''
  response = []
  cars = []

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  for association in user.cars:
    if (association.users_id == user_id):
      car_id = association.cars_id
      cars.append(Car.query.get(car_id))

  # This, of all things, crashes
  # print cars

  # Retrives cars
  for car in cars:
    car_props = {}
    for param_key in car_param_keys:
      car_props[param_key] = car.get(param_key)
    car_props['id'] = car.id
    response.append(car_props)
  return jsonify(cars=response)

@app.route('/users/<session_token>/cars', methods=['POST'])
def create_car(session_token):
  '''
  Route for POST /users/<session_token>/cars
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @license_plate -- license plate passed in the body of the request
    @manufacturer -- manufacturer passed in the body of the request
  Description:
    Creates a new car with license plate @license_plate and manufacturer
    @manufacturer. Appends the new car to the list of cars owned by the
    user associated with the session identifier @session_token.
  Returns:
    If validation succeeds -- created car
    If validation fails -- description of failure
  '''
  omitted = []
  invalid = []
  response = {}

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  # Validates car information
  if (not request.json):
    return 'Must provide %s\n' % ', '.join(car_param_keys), 400
  for param_key in car_param_keys:
    if (param_key not in request.json):
      omitted.append(param_key)
  if (len(omitted) > 0):
    return 'Must provide %s\n' % ', '.join(omitted), 400
  for param_key in car_param_keys:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)
  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  license_plate = request.json['license_plate']
  manufacturer = request.json['manufacturer']

  car = Car.query.filter_by(license_plate=license_plate).first()
  if (not car):
    # If car DNE, creates car
    car = Car(license_plate, manufacturer, user_id)
    if (not car):
      return 'Failed to create car\n', 400
  # Appends car to list of cars owned by user
  user_join_car = UsersJoinCars()
  user_join_car.car = car
  user.cars.append(user_join_car)

  db.add(car)
  db.commit()

  # Retrieves car
  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

@app.route('/users/<session_token>/cars/<car_id>', methods=['PUT'])
def update_car(sesion_token, car_id):
  '''
  Route for PUT /users/<session_token>/cars/<car_id>
  Accepts:
    @car_id -- car identifier passed in the route of the request
    @session_token -- valid identifier passed in the route of the request
    @license_plate -- optional license plate passed in the body of the request
    @manufacturer -- optional manufacturer passed in the body of the request
  Description:
    Updates an existing car with license plate @license_plate or manufacturer
    @manufacturer.
  Returns:
    If validation succeeds -- updates car
    If validation fails -- description of failure
  '''
  present = []
  invalid = []
  response = {}

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400
  cars = user.cars

  # Validates car_id
  try:
    car_id = int(car_id)
  except:
    return 'Invalid car_id %s' % car_id, 400

  # Validates user owns car
  if (car_id not in [car.id for car in cars]):
    return 'Invalid session_token %s' % session_token, 400

  # Validates car
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400

  # Validates updated car information
  for param_key in car_param_keys:
    if (param_key in request.json):
      present.append(param_key)
  if (len(present) == 0):
    return 'Must provide at least one parameter\n', 400
  for param_key in present:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)
  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  # Updates car
  for param_key in present:
    car.set(param_key, request.json[param_key])

  # Retrieves car
  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

@app.route('/users/<session_token>/cars/<car_id>', methods=['DELETE'])
def delete_car(session_token, car_id):
  '''
  Route for DELETE /users/<session_token>/cars/<car_id>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @car_id -- car identifier passed in the route of the request
  Description:
    Deletes an existing car with car identifier @car_id.
  Returns:
    If validation succeeds -- description of success
    If validation fails -- description of failure
  '''
  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400
  cars = user.cars

  # Validates car_id
  try:
    car_id = int(car_id)
  except:
    return 'Invalid car_id %s' % car_id, 400

  # Validates user owns car
  if (car_id not in [car.id for car in cars]):
    return 'Invalid session_token %s' % session_token, 400

  # Validates car
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400

  # Deletes car
  Car.query.filter_by(id=car_id).delete()

  return 'Delete successful', 200

#==============================================================================
#
#==============================================================================
@app.route('/users/identifier', methods=['POST'])
def create_identity_token():
  email_address = request.json['email_address']
  # Grab nonce from request
  nonce = request.json['nonce']

  user = User.query.filter_by(email_address=email_address).first()

  private_rsa_key = None
  # Read RSA key
  root = os.path.dirname(__file__)
  with open(os.path.join(root, '../..', 'layer.pem'), 'r') as rsa_priv_file:
    private_rsa_key = rsa_priv_file.read()

  print private_rsa_key
  # Create identity token
  # Make sure you have PyJWT and PyCrypto libraries installed and imported
  identityToken = jwt.encode(
    payload={
      'iss': '7b29a59c-db1b-11e4-b670-52bb02000413',  # The Layer Provider ID
      'prn': email_address,                               # String - Provider's internal ID for the authenticating user
      'iat': datetime.now(),                          # Integer - Time of Token Issuance in RFC 3339 seconds
      'exp': datetime.utcnow() + timedelta(seconds=30),   # Integer - Arbitrary time of Token Expiration in RFC 3339 seconds
      'nce': nonce                                    # The nonce obtained via the Layer client SDK.
    },
    key=private_rsa_key,
    algorithm='RS256',
    headers = {
      'typ': 'JWS',               # String - Expresses a MIME Type of application/JWS
      "alg": "RS256",             # String - Expresses the type of algorithm used to sign the token, must be RS256
      'cty': 'layer-eit;v=1',     # String - Express a Content Type of Layer External Identity Token, version 1
      'kid': '4d3def30-dc83-11e4-852c-52bb25003d93' # Sting - Layer Key ID used to sign the token
    }
  )

  response = {}
  user.set("participant_identifier", identityToken)
  response["participant_identifier"] = identityToken

  return jsonify(response)

#============================================================================
# Extra shit
#============================================================================
@app.route('/users/<session_token>/cars/<car_id>', methods=['GET'])
def get_car(session_token, car_id):
  '''
  Route for GET /users/<session_token>/cars/<car_id>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @car_id -- car identifier passed in the route of the request
  Returns:
    If validation succeeds -- car associated with the car identifier @car_id
    If validation fails -- description of failure
  '''
  response = {}

  # Validates session
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400
  cars = user.cars

  # Validates car_id
  try:
    car_id = int(car_id)
  except ValueError:
    return 'Invalid car_id %s' % car_id, 400

  # Validates user owns car
  if (car_id not in [car.id for car in cars]):
    return 'Invalid session_token %s' % session_token, 400

  # Validates car
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400

  # Retrieve car
  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

# User routes for Development
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