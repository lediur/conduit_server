import unittest

import os
import app as conduit 
import tempfile

import json
import csv

email_address_to_session_token = {}

class ConduitTests(unittest.TestCase):
  #============================================================================
  # Utilities
  #============================================================================
  def setUp(self):
    self.db_fd, conduit.app.config['DATABASE'] = tempfile.mkstemp()
    conduit.app.config['TESTING'] = True
    self.app = conduit.app.test_client()
    conduit.init_db()

  def tearDown(self):
    os.close(self.db_fd)
    os.unlink(conduit.app.config['DATABASE'])

  def import_entries(self, filename):
    entries = []
    with open(filename, 'rb') as csvFile:
      csvFileReader = csv.reader(csvFile, delimiter=',')
      isHeader = True
      headers = []
      for row in csvFileReader:
        if (isHeader):
          isHeader = False
          headers = row
        else:
          entry = {}
          for i in xrange(len(headers)):
            entry[headers[i]] = row[i]
          entries.append(entry)
    return entries

  def create_user(self, user):
    return self.app.post('/users', data=json.dumps(user),
                         content_type='application/json')

  def create_session(self, session):
    return self.app.post('/sessions', data=json.dumps(session),
                         content_type='application/json')

  def create_car(self, session_token, car):
    return self.app.post('/'.join(['', 'users', session_token, 'cars']),
                         data=json.dumps(car), content_type='application/json')

  #============================================================================
  # Tests
  #============================================================================
  def test_001(self):
    res = self.app.get('/')
    self.assertEquals(res.status, '200 OK')

  def test_002(self):
    users = self.import_entries('seed/users.csv')
    for user in users:
      res = self.create_user(user)
      self.assertEquals(res.status, '200 OK')

  def test_003(self):
    sessions = self.import_entries('seed/sessions.csv')
    for session in sessions:
      res = self.create_session(session)
      email_address_to_session_token[session['email_address']] = (json.loads(res.data))['session_token']
      self.assertEquals(res.status, '200 OK')

  def test_004(self):
    cars = self.import_entries('seed/cars.csv')
    for car in cars:
      email_address = car.pop('email_address')
      res = self.create_car(email_address_to_session_token[email_address], car)
      self.assertEquals(res.status, '200 OK')

if __name__ == '__main__':
  unittest.main()
