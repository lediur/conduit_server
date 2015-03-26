from flask import jsonify, request
from app import app
from app.database import db

from app.models import Conversation

import datetime

# Message routes
@app.route('/messages/<conversation_id>', methods=['GET'])
def message():
  conversation = Conversation.query.get(conversation_id)

  messages = [{
    'text': message.text,
    'timestamp': message.timestamp
  } for message in conversation.messages]
  return jsonify(messages=messages)

@app.route('/messages/create', methods=['POST'])
def message_create():
  text = request.json['text']
  timestamp = datetime.datetime.utcnow()
  
  conversation_id = int(request.json['conversation_id'])
  conversation = Conversation.query.get(conversation_id)

  m = Message(text, timestamp, conversation_id)
  conversation.messages.append(m)
  db.commit()
  
  message = {
    'text': m.text,
    'timestamp': m.timestamp,
    'conversation_id': m.conversation_id
  }
  return jsonify(message=message)

@app.route('/messages/update', methods=['POST'])
def message_update():
  return 'POST /messages/update\n'

@app.route('/messages/delete', methods=['POST'])
def message_delete():
  return 'POST /messages/delete\n'
