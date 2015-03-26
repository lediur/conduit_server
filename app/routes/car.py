from flask import jsonify, request
from app import app
from app.database import db

from app.models import Car

# Car routes
@app.route('/cars', methods=['GET'])
def car():
  cars = [{
    'id': car.id,
    'license_plate': car.license_plate,
    'manufacturer': car.manufacturer
  } for car in Car.query.all()]
  return jsonify(cars=cars)

@app.route('/cars/create', methods=['POST'])
def car_create():
  license_plate = request.json['license_plate']
  manufacturer  = request.json['manufacturer']

  c = Car(license_plate, manufacturer)
  db.add(c)
  db.commit()
  
  car = {
    'license_plate': c.license_plate,
    'manufacturer': c.manufacturer,
  }
  return jsonify(car=car)

@app.route('/cars/update', methods=['POST'])
def car_update():
  return 'POST /cars/update\n'

@app.route('/cars/delete', methods=['POST'])
def car_delete():
  return 'POST /cars/delete\n'
