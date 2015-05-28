from flask import jsonify, request
from app import app
from app.database import db

from app.models import Session, User

from app import utils
from app.utils import user_param_keys, session_param_keys, user_login_param_keys, validate

# Session routes for Production
@app.route('/sessions', methods=['POST'])
def create_session():
  '''
  If the request includes 'email_address' and 'password' as body parameters,
  returns the random UUID session token. Otherwise, returns 400 Bad Request
  Error.
  '''
  user_login_params, error = utils.validate_param_keys_exist(request, user_login_param_keys, len(user_login_param_keys))
  if (error):
    return jsonify(error=error), 400

  error = utils.validate_user_params(user_login_params)
  if (error):
    return jsonify(error=error), 400

  user, error = utils.try_retrieve_user(user_login_params)
  if (error):
    return jsonify(error=error), 400

  session, error = utils.try_create_session(user)
  if (error):
    return jsonify(error=error), 400

  response = utils.create_response(user, user_param_keys)

  return jsonify(session_token=session.get('session_token'), user=response)