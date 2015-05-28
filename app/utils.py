from app.database import db
from app.models import Car, Session, User

from passlib.hash import sha256_crypt
import datetime # try_create_session
import uuid # try_create_session

car_param_keys = ['license_plate', 'manufacturer']
conversation_param_keys = ['charger_unlocked', 'timestamp', 'receiver_car_id', 'requester_user_id']
message_param_keys = ['sender_id', 'text', 'timestamp', 'conversation_id']
session_param_keys = ['session_token', 'timestamp', 'user_id']
user_param_keys = ['email_address', 'first_name', 'last_name', 'password', 'phone_number', 'push_enabled']

user_login_param_keys = ['email_address', 'password']

#==============================================================================
# General utilities
#==============================================================================

def create_response(obj, param_keys):
  response = {}
  for param_key in param_keys:
    if (param_key != 'password'):
      response[param_key] = obj.get(param_key)
  return response

#==============================================================================
# Validation utilities
#==============================================================================

def validate(type, text):
  return True

def validate_param_keys_exist(request, param_keys, threshold):
  '''
  Accepts:
    @request -- HTTP request object
    @param_keys -- List of parameters to validate in the HTTP request object
    @threshold -- Threshold number of valid parameters to return success
  Description:
    Helper function to validate that @request contains at least @threshold
    parameters contained in @param_keys.
  Returns:
    If validation succeeds -- tuple (@params, None), such that @params 
      represents a dictionary from the subset of @param_keys contained
      in @request to their values
    If validation fails -- tuple (None, @error), such that @error contains
      a description of the failure and an HTTP error code to send
  '''
  param_keys_exist = []
  param_keys_absent = []
  params = {}

  if (not request.json):
    return None, {
      'message': 'Missing %s' % ', '.join(param_keys_absent),
      'code': 400
    }
  for param_key in param_keys:
    if (param_key not in request.json):
      param_keys_absent.append(param_key)
    else:
      param_keys_exist.append(param_key)
  if (len(param_keys_absent) > len(param_keys) - threshold):
    return None, {
      'message': 'Missing %s' % ', '.join(param_keys_absent), 
      'code': 400
    }
  for param_key in param_keys_exist:
    params[param_key] = request.json[param_key]

  return params, None

def validate_user_params(params):
  '''
  Description:
    Helper function to validate that @params contains valid parameters
    contained in @param_keys.
  '''
  invalid = []
  for param_key in params:
    try:
      user = User()
      user.set(param_key, params[param_key])
    except:
      invalid.append(param_key)
  if (len(invalid) > 0):
    return {'message': 'Invalid %s' % ', '.join(invalid), 'code': 400}
  return None

def validate_session(session_token):
  '''
  Description:
    Helper function to validate the session identified by @session_token.
  Returns:
    If validation succeeds -- tuple (user, None), such that @user specifies
      the user associated with the session
    If validation fails -- tuple (None, error), such that @error contains
      a description of the failure and an HTTP error code to send
  '''
  if (not session_token):
    return None, {'message': 'Must provide session_token', 'code': 400}
  session = Session.query.filter_by(session_token=session_token).first()
  if (not session):
    return None, {'message': 'Invalid session_token %s' % session_token, 'code': 400}
  user = User.query.get(session.user_id)
  if (not user):
    return None, {'message': 'Invalid session_token %s' % session_token, 'code': 400}
  return user, None

#==============================================================================
# Session utilities
#==============================================================================

def try_create_session(user):
  session_token = str(uuid.uuid4())
  timestamp = datetime.datetime.utcnow()
  user_id = user.id

  try:
    session = Session(session_token, timestamp, user_id)
    db.add(session)
    db.commit()
  except:
    db.rollback()
    return None, {'message': 'Failed to create session', 'code': 400}
  else:
    return session, None

#==============================================================================
# User utilities
#==============================================================================

def try_create_user(user_params):
  email_address = user_params['email_address']
  first_name = user_params['first_name']
  last_name = user_params['last_name']
  password = user_params['password']
  phone_number = user_params['phone_number']
  push_enabled = user_params['push_enabled']

  try:
    user = User(email_address, first_name, last_name, password, phone_number, push_enabled)
    db.add(user)
    db.commit()
  except:
    db.rollback()
    return None, {'message': 'Failed to create user', 'code': 400}
  else:
    return user, None

def try_update_user(user, user_params):
  for param_key in user_params:
    try:
      user.set(param_key, user_params[param_key])
      db.add(user)
      db.commit()
    except:
      db.rollback()
      return None, {'message': 'Failed to update user', 'code': 400}
  return user, None

def try_delete_user(user):
  try:
    User.query.filter_by(id=user.id).delete()
    db.commit()
  except:
    db.rollback()
    return {'message': 'Failed to delete user', 'code': 400}
  return None

def try_retrieve_user(user_login_params):
  email_address = user_login_params['email_address']
  password = user_login_params['password']

  user = User.query.filter_by(email_address=email_address).first()
  if (not user or not sha256_crypt.verify(password, user.password)):
    return None, {'message': 'Invalid login credentials', 'code': 400}
  else:
    return user, None

def try_encrypt_password(user_params):
  if ('password' in user_params):
    user_params['password'] = sha256_crypt.encrypt(user_params['password'])
  return user_params, None