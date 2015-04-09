from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, User

from app.utils import car_param_keys, validate

# Car routes
@app.route('/cars', methods=['GET'])
def get_cars():
  response = []
  cars = []

  if ('user_id' in request.args):
    user_id = request.args['user_id']
    cars = User.query.get(user_id).cars
  else:
    cars = Car.query.all()

  for car in cars:
    car_props = {}
    for param_key in car_param_keys:
      car_props[param_key] = car.get(param_key)
    car_props['id'] = car.id
    response.append(car_props)
  return jsonify(cars=response)

@app.route('/cars/<car_id>', methods=['GET'])
def get_cars_by_car_id(car_id):
  response = {}
  
  car_id = int(car_id)
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400

  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

@app.route('/cars/create', methods=['POST'])
def create_car():
  omitted = []
  invalid = []
  response = {}

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
  # user_id = request.json['user_id']

  car = Car(license_plate, manufacturer)
  if (not car):
    return 'Failed to create car\n', 400
  db.add(car)
  db.commit()
  
  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

@app.route('/cars/<car_id>/update', methods=['POST'])
def update_car(car_id):
  present = []
  invalid = []
  response = {}

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

  car_id = int(car_id)
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400

  for param_key in present:
    car.set(param_key, request.json[param_key])

  for param_key in car_param_keys:
    response[param_key] = car.get(param_key)
  response['id'] = car.id

  return jsonify(response)

@app.route('/cars/<car_id>/delete', methods=['POST'])
def delete_car(car_id):
  car_id = int(car_id)
  car = Car.query.get(car_id)
  if (not car):
    return 'Cannot find car_id %d\n' % car_id, 400
  Car.query.filter_by(id=car_id).delete()
  return '', 200
