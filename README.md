#Conduit Server
Server for Team Conduit

##Creating a Virtual Environment
```
$ virtualenv env
$ env/bin/pip install flask
$ env/bin/pip install flask-sqlalchemy
$ env/bin/pip install flask-wtf

$ env/bin/pip install jwt
```
##Running the App in the Virtual Environment
```
$ env/bin/python run.py
```
##Sending Requests with cURL
```
$ curl -H "Content-Type: application/json" -d '@user.json' 'localhost:8080/users'
$ curl -H "Content-Type: application/json" -d '@login.json' 'localhost:8080/sessions'
$ curl -H "Content-Type: application/json" -d '@car.json' 'localhost:8080/users/imma_session_token/cars'
```