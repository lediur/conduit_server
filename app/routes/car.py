from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, Session, User, UsersJoinCars

from app.utils import car_param_keys, validate

# Car routes for Production
@app.route('/users', methods=['GET'])
def get_users():
  '''
  If the request includes 'car_id' or 'license_plate' as a query string
  parameter, returns all owners of the car. Otherwise, returns all users.
  '''
  response = []
  users = []

  if ('car_id' in request.json):
    car_id = request.args['car_id']
    users = Car.query.get(car_id).users
  elif ('license_plate' in request.args):
    license_plate = request.args['license_plate']
    users = Car.query.filter_by(license_plate=license_plate)\
                     .first().users
  else:
    users = User.query.all()

  for user in users:
    user_props = {}
    for param_key in user_param_keys:
      user_props[param_key] = user.get(param_key)
    user_props['id'] = user.id
    response.append(user_props)
  return jsonify(users=response)