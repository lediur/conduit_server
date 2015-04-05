from flask import jsonify, request
from app import app
from app.database import db

from app.models import Conversation

from app.utils import message_param_keys, validate
import datetime

# Message routes
# @route /messages -- list of all messages
# @route /messages?conversation_id=<id> -- list of all messages in conversation
#        specified by conversation_id id
@app.route('/messages', methods=['GET'])
def get_messages():
  response = []
  messages = []

  if ('conversation_id' in request.args):
    conversation_id = request.args['conversation_id']
    messages = Conversation.query.get(conversation_id).messages
  else:
    messages = Message.query.all()

  for message in messages:
    message_props = {}
    for param_key in message_param_keys:
      message_props[param_key] = message.get(param_key)
    message_props['id'] = message.id
    response.append(message_props)
  return jsonify(messages=response)

@app.route('/messages/<message_id>', methods=['GET'])
def get_messages_by_message_id(message_id):
  response = {}
  
  message_id = int(message_id)
  message = Message.query.get(message_id)
  if (not message):
    return 'Cannot find message_id %d\n' % message_id, 400

  for param_key in message_param_keys:
    response[param_key] = message.get(param_key)
  response['id'] = message.id

  return jsonify(response)

@app.route('/messages/create', methods=['POST'])
def create_message():
  omitted = []
  invalid = []
  response = {}

  for param_key in message_param_keys:
    if (param_key not in request.json):
      omitted.append(param_key)

  if (len(omitted) > 0):
    return 'Must provide %s\n' % ', '.join(omitted), 400

  for param_key in message_param_keys:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400
  
  sender_id = request.json['sender_id']
  text = request.json['text']
  timestamp = datetime.datetime.utcnow()
  conversation_id = request.json['conversation_id']

  message = Message(sender_id, text, timestamp, conversation_id)
  if (not message):
    return 'Failed to create message\n', 400
  db.add(message)
  conversation = Conversation.query.get(conversation_id)
  conversation.messages.append(message)
  db.commit()
  
  for param_key in message_param_keys:
    response[param_key] = message.get(param_key)
  response['id'] = message.id

  return jsonify(response)

@app.route('/messages/update/<message_id>', methods=['POST'])
def update_message(message_id):
  present = []
  invalid = []
  response = {}

  for param_key in message_param_keys:
    if (param_key in request.json):
      present.append(param_key)

  if (len(present) == 0):
    return 'Must provide at least one parameter\n', 400

  for param_key in present:
    if (not validate(param_key, request.json[param_key])):
      invalid.append(param_key)

  if (len(invalid) > 0):
    return 'Invalid %s\n' % ', '.join(invalid), 400

  message_id = int(message_id)
  message = Message.query.get(message_id)
  if (not message):
    return 'Cannot find message_id %d\n' % message_id, 400

  for param_key in present:
    message.set(param_key, request.json[param_key])

  for param_key in message_param_keys:
    response[param_key] = message.get(param_key)
  response['id'] = message.id

  return jsonify(response)

@app.route('/messages/delete/<message_id>', methods=['POST'])
def delete_message(message_id):
  message_id = int(message_id)
  message = Message.query.get(message_id)
  if (not message):
    return 'Cannot find message_id %d\n' % message_id, 400
  Message.query.filter_by(id=message_id).delete()
  return '', 200