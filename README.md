#Conduit Server
Server for Team Conduit

##Creating a Virtual Environment
```
$ virtualenv env
$ env/bin/pip install flask
$ env/bin/pip install flask-sqlalchemy
$ env/bin/pip install flask-wtf
```
##Running the App in the Virtual Environment
```
$ env/bin/python run.py
```
##Sending Requests with cURL
```
$ curl -H "Content-Type: application/json" -d '@body.json' 'localhost:8080/user/create'
```