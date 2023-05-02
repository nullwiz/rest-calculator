# restcalculator challange
## Overview
This is a simple flask app that relies mostly on it's makefile. 
It implements the factory pattern https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/
and the unit of work pattern to address concerns related to managing and organizing db operations, particularly transactions, aswell as centralizing context. 
There are also services and entrypoints (controllers) for each porpuse. 
Its also, dockerized. It provides filtering/selecting for the resources,
A client user is created by default by logging in with a policy-compliant password. The admin user can be created
using the postman collection. It's important to check that the proper CSRF token was added while using the postman collection,
for this the login prequests provide a test that automatically set's the X-CSRF-TOKEN variable. 


## Default credentials
```
Client
======
email: defaultclient@client.as
password: Test1234!

Admin
=====
email: defaultadmin@admin.as
passowrd: adminpass

```

Login automatically creates your account if it meets the requirements for a user. 
You can also create an admin thru the admin panel with the Postman collection.
Only admins can change resources and can see all records. 
Clients can see their records, but not modify resources. 


## Setup 

- Clone the repo and create a local environment & activate

- Run makefile 

This can either be:

```make all``` 
builds containers, runs the tests
```make deploy```
deploys to serverless (more on this later)
```make e2e-tests```
runs e2e tests
``` make package```
uninstalls and reinstall the  the wheel package locally
``` make up```
runs containers
``` make build-local-db```
re-creates db with starting credentials
``` make build-prod-db```
in order to make this safe, this expects that we do:
``` ~: make build-prod-db db='postgresql+psycopg2://{user}:{password}@database-1.cypgxjiydrat.us-east-1.rds.amazonaws.com/postgres'```
so to do that in prod you need to pass an env variable directly in the command line. 

## Postman Collection
It's important to set the variables for the collection commited to this repository in the folder postman/ 
Import the collection and set the envs:
For prod:
URL ={urprodurl}
X-CSRF-TOKEN (blank, will be set by the test when logging in, but needs to be defined)

With that set, you should be good to go!

## Deployment

Deployment has the limitation that, because it's using RDS, I have not figured out a way of automatically setting up the DB 
with serverless (it was my first time using it). 
However, if you create a RDS instance, the deployment pre-action expects the following variables to be present in the .env
in the root directory:

JWT_SECRET_KEY={your_jwt_secret}
AWS_PGSQL_PATH=postgresql+psycopg2://{user}:{password}@{db}/postgres
CLIENT_PASSWORD={client_password}
ADMIN_PASSWORD={admin_password}
FRONTEND_URL={frontend_url}
CONFIG_TYPE=production
DUMMY_VAR=1

If the connection is available, and with those vars set in the env file, deploying is as simple as doing

```
    make deploy
```


## Queue for processing operations 

Handling a big list of operations from a CSV file for a user is possible, given it has enough credits to handle it. 
For that, there is an S3 bucket along with a SQS queue, and a worker lambda function that 
you can find in the worker/ subdirectory.

S3 bucket : localhost:4566/buckeeto
SQS queue : http://localhost:4566/000000000000/opworker