#Conduit Server
Server for Team Conduit

##Creating a Virtual Environment
```
$ virtualenv env
$ env/bin/pip install flask
$ env/bin/pip install flask-sqlalchemy
$ env/bin/pip install flask-wtf

$ env/bin/pip install jwt
$ env/bin/pip install cryptography
```
##Running the App in the Virtual Environment
```
$ env/bin/python run.py
```
##Sending Requests with cURL
```
$ curl -H "Content-Type: application/json" -X POST -d '@create_user.json' 'localhost:1337/users'
$ curl -H "Content-Type: application/json" -X POST -d '@login.json' 'localhost:1337/sessions'
$ curl -H "Content-Type: application/json" -X PUT -d '@update_user.json' 'localhost:1337/users/[session_token]'
$ curl -X DELETE 'localhost:1337/users/[session_token]'
$ curl -H "Content-Type: application/json" -d '@car.json' 'localhost:1337/users/[session_token]/cars'
```
##View the Database
```
$ env/bin/python
>>> from app.models import User
>>> User.query.all() 