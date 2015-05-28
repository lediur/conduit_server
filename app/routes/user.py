from flask import jsonify, request, session
from app import app
from app.database import db

from app.models import Car, Session, User, UsersJoinCars

from app import utils
from app.utils import car_param_keys, user_param_keys, validate

import Crypto
import jwt
from Crypto.PublicKey import RSA
import os
from datetime import *
from passlib.hash import sha256_crypt

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
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error)

  response = utils.create_response(user, user_param_keys)
  return jsonify(response)

@app.route('/users', methods=['POST'])
def create_user():
  '''
  Route for POST /users
  Accepts:
    @email_address, @first_name, @last_name, @password, @phone_number,
      @push_enabled -- required parameters passed in the body of the request
  Description:
    Creates a new user with @email_address, @first_name, @last_name, 
      @password, @phone_number, and @push_enabled
  Returns:
    If validation succeeds -- created user
    If validation fails -- description of failure
  '''
  user_params, error = utils.validate_param_keys_exist(request, user_param_keys, len(user_param_keys))
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_params(user_params)
  if (error):
    return jsonify(error=error), 400

  user_params, error = utils.try_encrypt_password(user_params)
  if (error):
    return jsonify(error=error), 400

  user, error = utils.try_create_user(user_params)
  if (error):
    return jsonify(error=error), 400

  response = utils.create_response(user, user_param_keys)
  return jsonify(response)

@app.route('/users/<session_token>', methods=['PUT'])
def update_user(session_token):
  '''
  Route for PUT /users/<session_token>
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @email_address, @first_name, @last_name, @password, @phone_number,
      @push_enabled -- optional params passed in the body of the request,
      must specify at least one
  Description:
    Updates an existing user with email address @email_address, first name
    @first_name, last name @last_name, password @password, phone number
    @phone_number, or push enabled @push_enabled.
  Returns:
    If validation succeeds -- updates user
    If validation fails -- description of failure
  '''
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400

  user_params, error = utils.validate_param_keys_exist(request, user_param_keys, 1)
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_params(user_params)
  if (error):
    return jsonify(error=error), 400

  user_params, error = utils.try_encrypt_password(user_params)
  if (error):
    return jsonify(error=error), 400

  user, error = utils.try_update_user(user, user_params)
  if (error):
    return jsonify(error=error), 400

  response = utils.create_response(user, user_param_keys)
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
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400

  error = utils.try_delete_user(user)
  if (error):
    return jsonify(error=error), 400
  
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
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400

  cars, error = utils.try_retrieve_cars_of_user(user)
  if (error):
    return jsonify(error=error), 400

  response = []
  for car in cars:
    response.append(utils.create_response(car, car_param_keys))
  return jsonify(cars=response)

@app.route('/users/<session_token>/cars', methods=['POST'])
def create_car(session_token):
  '''
  Route for POST /users/<session_token>/cars
  Accepts:
    @session_token -- valid identifier passed in the route of the request
    @license_plate, @manufacturer -- required parameters passed in the body
      of the request
  Description:
    Creates a new car with license plate @license_plate and manufacturer
    @manufacturer. Appends the new car to the list of cars owned by the
    user associated with the session identifier @session_token.
  Returns:
    If validation succeeds -- created car
    If validation fails -- description of failure
  '''

  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400

  car_params, error = utils.validate_param_keys_exist(request, car_param_keys, len(car_param_keys))
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_car_params(car_params)
  if (error):
    return jsonify(error=error), 400

  user, error = utils.try_create_user(user_params)
  if (error):
    return jsonify(error=error), 400

  car, error = utils.try_create_car_of_user(user, car_params)
  if (error):
    return jsonify(error=error), 400

  response = utils.create_response(car, car_param_keys)
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
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400
  cars = user.cars

  car_id, error = utils.try_cast_to_int('car_id', car_id)
  if (error):
    return jsonify(error=error), 400

  car, error = utils.try_retrieve_car_by_id(car_id)
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_owns_car(cars, car_id)
  if (error):
    return jsonify(error=error), 400

  car_params, error = utils.validate_param_keys_exist(request, car_param_keys, 1)
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_car_params(car_params)
  if (error):
    return jsonify(error=error), 400

  car, error = utils.try_update_car(car, car_params)
  if (error):
    return jsonify(error=error), 400

  response = utils.create_response(car, car_param_keys)
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
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400
  cars = user.cars

  car_id, error = utils.try_cast_to_int('car_id', car_id)
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_owns_car(cars, car_id)
  if (error):
    return jsonify(error=error), 400

  car, error = utils.try_retrieve_car_by_id(car_id)
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_owns_car(cars, car_id)
  if (error):
    return jsonify(error=error), 400

  error = utils.try_delete_car(car)
  if (error):
    return jsonify(error=error), 400

  # TODO Delete associations with car
  
  return '', 200

#==============================================================================
#
#==============================================================================
@app.route('/users/identity', methods=['POST'])
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
  response["identity"] = identityToken
  # Note: This should NOT be persisted on the client or server.

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
    return jsonify(error={'message': 'Must provide session_token', 'code': 400})
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return jsonify(error={'message': 'Invalid session_token %s' % session_token, 'code': 400})
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return jsonify(error={'message': 'Invalid session_token %s' % session_token, 'code': 400})
  cars = user.cars

  # Validates car_id
  try:
    car_id = int(car_id)
  except ValueError:
    return jsonify(error={'message': 'Invalid car_id %s' % car_id, 'code': 400})

  # Validates user owns car
  if (car_id not in [car.id for car in cars]):
    return jsonify(error={'message': 'Invalid session_token %s' % session_token, 'code': 400})

  # Validates car
  car = Car.query.get(car_id)
  if (not car):
    return jsonify(error={'message': 'Cannot find car_id %d\n' % car_id, 'code': 400})

  # Retrieve car
  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

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
    return jsonify(error={'message': 'Cannot find user_id %d\n' % user_id, 'code': 400})

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)