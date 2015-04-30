from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, Session, User

from app.utils import car_param_keys, user_param_keys, validate

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
  
  for user in User.query.all():
    for join in user.cars:
      if Car.query.get(join.cars_id).license_plate == license_plate:
        users.append(user)

  for user in users:
    user_props = {}
    for param_key in user_param_keys:
      user_props[param_key] = user.get(param_key)
    user_props['id'] = user.id
    user_props['participant_identifier'] = user.participant_identifier
    response.append(user_props)
  return jsonify(users=response)