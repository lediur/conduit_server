from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, Session, User

from app.utils import car_param_keys, user_param_keys, validate

@app.route('/', methods=['GET'])
def main():
  return "No entries here so far", 200

# Car routes for Production
@app.route('/cars/<license_plate>/users', methods=['GET'])
def get_subscribers(license_plate):
  response = []
  users = []

  # Validates session
  session_token = request.args['session_token']
  if (not session_token):
    return 'Must provide session_token', 400
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return 'Invalid session_token %s' % session_token, 400
  user_id = session.user_id
  user = User.query.get(user_id)
  if (not user):
    return 'Invalid session_token %s' % session_token, 400

  # Validates license plate
  if (not license_plate):
    return 'Must provide license_plate', 400
  car = Car.query.filter_by(license_plate=license_plate).first()
  if (not car):
    return 'Invalid license_plate %s' % license_plate, 400
  car_id = car.id

  for association in car.users:
    if (association.cars_id == car_id):
      user_id = association.users_id
      users.append(User.query.get(user_id))

  for user in users:
    user_props = {}
    for param_key in user_param_keys:
      user_props[param_key] = user.get(param_key)
    response.append(user_props)

  return jsonify(users=response)