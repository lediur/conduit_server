from app.database import db
from app.models import Car, Session, User

from passlib.hash import sha256_crypt
import datetime # try_create_session
import uuid # try_create_session

car_param_keys = ['license_plate', 'manufacturer']
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

def try_cast_to_int(key, value):
  try:
    i = int(value)
  except ValueError:
    return None, {'message': 'Invalid %s %s' % (key, value), 'code': 400}
  return i, None

#==============================================================================
# Validation utilities
#==============================================================================
def validate(type, text):
  return True

def validate_param_keys_exist(request, param_keys, threshold):
  '''
  Description:
    Validates that @request contains at least @threshold parameters
      contained in @param_keys
  Returns:
    If validation succeeds -- tuple (@params, None)
      @params -- dictionary from the subset of @param_keys contained
                 in @request to their values
    If validation fails -- tuple (None, @error)
      @error -- description of the failure and HTTP error code
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

def validate_user_params(user_params):
  '''
  Description:
    Validates that @user_params contains valid user parameters, as dictated
      by the User model
  Returns:
    If validation succeeds -- None
    If validation fails -- description of the failure and HTTP error code
  '''
  invalid = []
  for param_key in user_params:
    try:
      user = User()
      user.set(param_key, user_params[param_key])
    except:
      invalid.append(param_key)
  if (len(invalid) > 0):
    return {'message': 'Invalid %s' % ', '.join(invalid), 'code': 400}
  return None

def validate_car_params(car_params):
  '''
  Description:
    Validates that @car_params contains valid car parameters, as dictated
      by the Car model
  Returns:
    If vaildation succeeds -- None
    If validation fails -- description of the failure and HTTP error code
  '''
  invalid = []
  for param_key in car_params:
    try:
      car = Car()
      car.set(param_key, car_params[param_key])
    except:
      invalid.append(param_key)
  if (len(invalid) > 0):
    return {'message': 'Invalid %s' % ', '.join(invalid), 'code': 400}
  return None

def validate_session(session_token):
  '''
  Description:
    Validates @session_token
  Returns:
    If validation succeeds -- tuple (@user, None)
      @user -- user associated with the session
    If validation fails -- tuple (None, @error)
      @error -- description of the failure and HTTP error code
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

def validate_user_owns_car(cars, car_id):
  '''
  Description:
    Validates @cars contains a car with @car_id
  Returns:
    If validation succeeds -- None
    If validation fails -- description of the failure and HTTP error code
  '''
  if (car_id not in [car.id for car in cars]):
    return {'message': 'Invalid session_token %s' % session_token, 'code': 400}
  return None

#==============================================================================
# Session utilities
#==============================================================================
def try_create_session(user):
  '''
  Description:
    Tries to create a session for @user
  Returns:
    If create succeeds -- tuple (@session, None)
      @session -- created session
    If create fails -- tuple (None, @error)
      @error -- description of the failure and HTTP error code
  '''
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
  '''
  Description:
    Tries to create a user with @user_params
  Returns:
    If create succeeds -- tuple (@user, None)
      @user -- created user
    If create fails -- tuple (None, @error)
      @error -- description of the failure and HTTP error code
  '''
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
  '''
  Description:
    Tries to update @user with @user_params
  Returns:
    If update succeeds -- tuple (@user, None)
      @user -- updated user
    If update fails -- tuple (None, @error)
      @error -- description of the failure and HTTP error code
  '''
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
  '''
  Description:
    Tries to delete @user
  Returns:
    If delete succeeds -- None
    If delete fails -- description of the failure and HTTP error code
  '''
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

def try_retrieve_cars_of_user(user):
  cars = []
  for association in user.cars:
    if (association.users_id == user.id):
      try:
        car_id = association.cars_id
        cars.append(Car.query.get(car_id))
      except:
        return None, {'message': 'Failed to retrieve cars of user', 'code': 400}
  return cars, None

def try_retrieve_users_of_car(car):
  users = []
  for association in car.users:
    if (association.cars_id == car.id):
      try:
        user_id = association.users_id
        users.append(User.query.get(user_id))
      except:
        return None, {'message': 'Failed to retrieve users of car', 'code': 400}
  return users, None

def try_encrypt_password(user_params):
  if ('password' in user_params):
    user_params['password'] = sha256_crypt.encrypt(user_params['password'])
  return user_params, None

#==============================================================================
# Car utilities
#==============================================================================
def try_create_car_of_user(user, car_params):
  license_plate = car_params['license_plate']
  manufacturer = car_params['manufacturer']

  car = Car.query.filter_by(license_plate=license_plate).first()
  if (not car):
    # If car DNE, creates car
    car = Car(license_plate, manufacturer, user.id)

  try:
    # Appends car to list of cars owned by user
    user_join_car = UsersJoinCars()
    user_join_car.car = car
    user.cars.append(user_join_car)

    db.add(car)
    db.commit()
  except:
    return None, {'message': 'Failed to create car', 'code': 400}
  else:
    return car, None

def try_retrieve_car_by_id(car_id):
  car = Car.query.get(car_id)
  if (not car):
    return None, {'message': 'Invalid car_id %d' % car_id, 'code': 400}
  return car, None

def try_retrieve_car_by_license_plate(license_plate):
  if (not license_plate):
    return None, {'message': 'Missing license_plate', 'code': 400}
  car = Car.query.filter_by(license_plate=license_plate).first()
  if (not car):
    return None, {'message': 'Invalid license_plate %s' % license_plate, 'code': 400}
  return car, None

def try_delete_car(car):
  try:
    Car.query.filter_by(id=car.id).delete()
    db.commit()
  except:
    db.rollback()
    return {'message': 'Failed to delete car', 'code': 400}
  return None