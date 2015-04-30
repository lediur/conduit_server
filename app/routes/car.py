from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, Session, User, UsersJoinCars

from app.utils import car_param_keys, validate

# Car routes for Production
@app.route('/cars/<session_token>', methods=['GET'])
def get_cars(session_token):
  '''
  Route for GET /cars.
  Accepts:
    @session_token -- valid identifier passed in the body of the request
  Returns:
    If validation succeeds -- list of cars owned by the user associated with
      the session given by @session_token.
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

@app.route('/cars/<car_id>', methods=['GET'])
def get_cars_by_car_id(car_id):
  '''
  Route for GET /cars/<car_id>
  Accepts:
    @car_id -- car identifier passed in the route of the request
    @session_token -- valid identifier passed in the body of the request
  Returns:
    If validation succeeds -- car associated with the car identifier @car_id
    If validation fails -- description of failure
  '''
  response = {}

  # Validates session
  if (not request.json):
    return 'Must provide session_token', 400
  if ('session_token' not in request.json):
    return 'Must provide session_token', 400
  session_token = request.json['session_token']
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

@app.route('/<session_token>/cars/create', methods=['POST'])
def create_car(session_token):
  '''
  Route for POST /cars/create
  Accepts:
    @session_token -- valid identifier passed in the body of the request
    @license_plate -- license plate passed in the body of the request
    @manufacturer -- manufacturer passed in the body of the request
  Description:
    Creates a new car with license plate @license_plate and manufacturer
    @manufacturer. Appends the new car to the list of cars owned by the
    user associated with the session given by @session_token.
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

@app.route('/cars/<car_id>/update', methods=['POST'])
def update_car(car_id):
  '''
  Route for POST /cars/<car_id>/update
  Accepts:
    @car_id -- car identifier passed in the route of the request
    @session_token -- valid identifier passed in the body of the request
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
  if ('session_token' not in request.json):
    return 'Must provide session_token', 400
  session_token = request.json['session_token']
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

  # Validates updated information for car
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

@app.route('/cars/<car_id>', methods=['DELETE'])
def delete_car(car_id):
  '''
  Route for DELETE /cars/<car_id>
  Accepts:
    @car_id -- car identifier passed in the route of the request
    @session_token -- valid identifier passed in the body of the request
  Description:
    Deletes an existing car with car identifier @car_id.
  Returns:
    If validation succeeds -- description of success
    If validation fails -- description of failure
  '''
  # Validates session
  if ('session_token' not in request.json):
    return 'Must provide session_token', 400
  session_token = request.json['session_token']
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