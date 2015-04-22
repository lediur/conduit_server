from flask import jsonify, request
from app import app
from app.database import db

from app.models import Session, User

from app.utils import user_param_login_keys, validate

import datetime
import uuid

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

  email_address = request.json['email_address']
  password = request.json['password']

  u = User.query.filter_by(email_address=email_address)\
                .filter_by(password=password)\
                .first()

  session_token = str(uuid.uuid4())
  timestamp = datetime.datetime.utcnow()
  user_id = u.id

  session = Session(session_token, timestamp, user_id)
  if (not session):
    return 'Failed to create session\n', 400
  return session.get('session_token')