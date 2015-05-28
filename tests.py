import unittest
from flask.ext.testing import TestCase

import os
import app as conduit 
import tempfile

import json

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

  def create_user(self, email_address, first_name, last_name, password,
                  phone_number, push_enabled):
    headers = [('Content-Type', 'application/json')]
    user = {
      'email_address': email_address,
      'first_name': first_name,
      'last_name': last_name,
      'password': password,
      'phone_number': phone_number,
      'push_enabled': push_enabled
    }
    return self.app.post('/users', data=json.dumps(user),
                         content_type='application/json')

  #============================================================================
  # Tests
  #============================================================================
  def test_001(self):
    res = self.app.get('/')
    self.assertEquals(res.status, "200 OK")

  def test_002(self):
    res = self.create_user('david@gmail.com', 'David', 'Eng', 'deng', '4086881441', '1')
    self.assertEquals(res.status, "200 OK")

if __name__ == '__main__':
  unittest.main()
