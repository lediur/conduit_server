from flask import abort, jsonify, request
from app import app
from app.database import db

from app.models import Car
from app.models import Conversation
from app.models import User

from app.utils import conversation_param_keys, validate
import datetime

# Conversation routes
@app.route('/conversations', methods=['GET'])
def get_conversations():
  response = []
  conversations = []

  if ('requester_user_id' in request.args):
    requester_user_id = request.args['requester_user_id']
    conversations = User.query.get(requester_user_id).conversations
  elif ('receiver_car_id' in request.args):
    receiver_car_id = request.args['receiver_car_id']
    conversations = Car.query.get(receiver_car_id).conversations
  else:
    conversations = Conversation.query.all()

  for conversation in conversations:
    conversation_props = {}
    for param_key in conversation_param_keys:
      conversation_props[param_key] = conversation.get(param_key)
    conversation_props['id'] = conversation.id
    response.append(conversation_props)
  return jsonify(conversations=response)

@app.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversations_by_conversation_id(conversation_id):
  response = {}
  
  conversation_id = int(conversation_id)
  conversation = Conversation.query.get(conversation_id)
  if (not conversation):
    return 'Cannot find conversation_id %d\n' % conversation_id, 400

  for param_key in conversation_param_keys:
    response[param_key] = conversation.get(param_key)
  response['id'] = conversation.id

  return jsonify(response)

@app.route('/conversations/create', methods=['POST'])
def create_conversation():
  omitted = []
  invalid = []
  response = {}

  for param_key in conversation_param_keys:
    if (param_key not in request.json):
      omitted.append(param_key)

  if (len(omitted) > 0):
    return 'Must provide %s\n' % ', '.join(omitted), 400

  for param_key in conversation_param_keys:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400
  
  charger_unlocked = request.json['charger_unlocked']
  timestamp = datetime.datetime.utcnow()
  receiver_car_id = request.json['receiver_car_id']
  requester_user_id = request.json['requester_user_id']

  conversation = Conversation(charger_unlocked, timestamp, receiver_car_id, requester_user_id)
  if (not conversation):
    return 'Failed to create conversation\n', 400
  db.add(conversation)
  receiver_car = Car.query.get(receiver_car_id)
  receiver_car.conversations.append(conversation)
  
  requester_user = User.query.get(requester_user_id)
  requester_user.conversations.append(conversation)
  db.commit()
  
  for param_key in conversation_param_keys:
    response[param_key] = conversation.get(param_key)
  response['id'] = conversation.id

  return jsonify(response)

@app.route('/conversations/<conversation_id>/update', methods=['POST'])
def update_conversation(conversation_id):
  present = []
  invalid = []
  response = {}

  for param_key in conversation_param_keys:
    if (param_key in request.json):
      present.append(param_key)

  if (len(present) == 0):
    return 'Must provide at least one parameter\n', 400

  for param_key in present:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  conversation_id = int(conversation_id)
  conversation = Conversation.query.get(conversation_id)
  if (not conversation):
    return 'Cannot find conversation_id %d\n' % conversation_id, 400

  for param_key in present:
    conversation.set(param_key, request.json[param_key])

  for param_key in conversation_param_keys:
    response[param_key] = conversation.get(param_key)
  response['id'] = conversation.id

  return jsonify(response)

@app.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
  conversation_id = int(conversation_id)
  conversation = Conversation.query.get(conversation_id)
  if (not conversation):
    return 'Cannot find conversation_id %d\n' % conversation_id, 400
  Conversation.query.filter_by(id=conversation_id).delete()
  return '', 200