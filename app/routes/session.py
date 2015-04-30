from flask import jsonify, request
from app import app
from app.database import db

from app.models import Session, User

from app.utils import user_param_keys, session_param_keys, user_param_login_keys, validate

import datetime
import uuid

# Session routes for Production
@app.route('/session/<session_token>', methods=['GET'])
def get_users_by_session_token(session_token):
  '''
  If the request includes 'session_token' as route string parameter, returns the
  corresponding user for that session token. Otherwise, returns 400 Bad Request Error.
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

  for param_key in user_param_keys:
    response[param_key] = user.get(param_key)
  response['id'] = user.id

  return jsonify(response)

@app.route('/sessions/create', methods=['POST'])
def create_session():
  '''
  If the request includes 'email_address' and 'password' as body parameters,
  returns the random UUID session token. Otherwise, returns 400 Bad Request
  Error.
  '''

  omitted = []
  invalid = []
  response = {}

  # Validation
  for param_key in user_param_login_keys:
    if (param_key not in request.json):
      omitted.append(param_key)
  if (len(omitted) > 0):
    return 'Must provide %s\n' % ', '.join(omitted), 400
  for param_key in user_param_login_keys:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)
  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  # Retrive user
  email_address = request.json['email_address']
  password = request.json['password']

  user = User.query.filter_by(email_address=email_address)\
                   .filter_by(password=password)\
                   .first()

  if (not user):
    return 'Invalid login credentials', 400

  # Create session
  session_token = str(uuid.uuid4())
  timestamp = datetime.datetime.utcnow()
  user_id = user.id

  session = Session(session_token, timestamp, user_id)
  if (not session):
    return 'Failed to create session\n', 400
  db.add(session)
  db.commit()

  user_props = {}
  for param_key in user_param_keys:
    user_props[param_key] = user.get(param_key)
  user_props['id'] = user.id
  user_props['participant_identifier'] = user.participant_identifier

  return jsonify(session_token=session.get('session_token'), user=user_props)

# Session routes for Development
@app.route('/sessions', methods=['GET'])
def get_sessions():
  response = []
  sessions = []

  sessions = Session.query.all()

  for session in sessions:
    session_props = {}
    for param_key in session_param_keys:
      session_props[param_key] = session.get(param_key)
    session_props['id'] = session.id
    response.append(session_props)
  return jsonify(sessions=response)