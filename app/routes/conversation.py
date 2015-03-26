from flask import abort, jsonify, request
from app import app
from app.database import db

from app.models import Car
from app.models import Conversation
from app.models import User

import datetime

# Conversation routes
@app.route('/conversations/<user_id>', methods=['GET'])
def conversation(user_id):
  user = User.query.get(user_id)

  if user:
    conversations = [{
      'id': conversation.id,
      'charger_unlocked': conversation.charger_unlocked,
      'request_lat': conversation.request_lat,
      'request_lng': conversation.request_lng,
      'timestamp': conversation.timestamp,
      'receiver_car_id': conversation.receiver_car_id,
      'requester_user_id': conversation.requester_user_id
    } for conversation in user.conversations]
    return jsonify(conversations=conversations)
  else:
    return abort(404)

@app.route('/conversations/create', methods=['POST'])
def conversation_create():
  charger_unlocked = (request.json['charger_unlocked'] == "True")
  request_lat = request.json['request_lat']
  request_lng = request.json['request_lng']
  timestamp = datetime.datetime.utcnow()

  receiver_car_id = int(request.json['receiver_car_id'])
  requester_user_id = int(request.json['requester_user_id'])
  receiver_car = Car.query.get(receiver_car_id)
  requester_user = User.query.get(requester_user_id)

  c = Conversation(charger_unlocked, request_lat, request_lng, timestamp, receiver_car_id, requester_user_id)
  receiver_car.conversations.append(c)
  requester_user.conversations.append(c)

  db.commit()
  
  conversation = {
    'charger_unlocked': c.charger_unlocked,
    'request_lat': c.request_lat,
    'request_lng': c.request_lng,
    'timestamp': c.timestamp,
    'receiver_car_id': c.receiver_car_id,
    'requester_car_id': c.requester_user_id
  }
  return jsonify(conversation=conversation)

@app.route('/conversations/update', methods=['POST'])
def conversation_update():
  return 'POST /conversations/update\n'

@app.route('/conversations/delete', methods=['POST'])
def conversation_delete():
  return 'POST /conversations/delete\n'
