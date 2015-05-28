from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car, Session, User

from app import utils
from app.utils import car_param_keys, user_param_keys, validate

@app.route('/', methods=['GET'])
def main():
  return "No entries here so far", 200

# Car routes for Production
@app.route('/cars/<license_plate>/users', methods=['GET'])
def get_subscribers(license_plate):
  session_token = request.args['session_token']
  user, error = utils.validate_session(session_token)
  if (error):
    return jsonify(error=error), 400

  car, error = utils.try_retrieve_car_by_license_plate(license_plate)
  if (error):
    return jsonify(error=error), 400  

  users, error = try_retrieve_users_of_car(car)
  if (error):
    return jsonify(error=error), 400

  response = []
  for user in users:
    response.append(utils.create_response(user, user_param_keys))

  return jsonify(users=response)