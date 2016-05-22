# Introduction

This is an example setup of flask/uwsgi/nginx running in a docker container.

It is intended as a starting place for backend api services; the app
supports JWT for authentication and CORS.

There are two dockerfiles:
 * flask-dockerfile: builds python, flask, uwsgi and nginx
   * this is based on the phusion baseimage because flask needs both nginx and uwsgi
     processes to be running and the phusion baseimage provides an init system.
   * if you want to configure your own setup, this is a good image to start with
   * TODO: if there is a phusion image with a recent version (2.7.11) of python, should
     use that instead of building our own
 * api-website-dockerfile
   * adds postgres support and sqlalchemy
   * adds flask extensions for JWT and CORS
   * configures nginx and uswsgi

The app itself is very basic. There are three endpoints:
 * POST /api/auth: uses the auth endpoint from https://pythonhosted.org/Flask-JWT/
 * GET /api/user/whoami: a protected endpoint that returns the username of the user corresponding to the sent authentication token
 * POST /api/user/register: register a new user

# Usage

### Build the images

```
$ cd dockerfiles
$ docker build -f flask-dockerfile -t flask .
$ docker build -f api-website-dockerfile -t flask-api .
$ cd ..
```

### Setup the database

In order to run the app, a database needs to be setup; I like to
use the postgres docker image:

```
$ docker run --name myapp-db -e POSTGRES_PASSWORD=mydbpassword -d -p 5432:5432 postgres
```

You'll want to create a new database and user, which can be done manually using psql:

```
$ psql -U postgres -p 5432 -h localhost <<EOF
CREATE USER dbuser WITH PASSWORD 'dbpwd';
CREATE DATABASE myapp WITH OWNER dbuser;
EOF
```

### Run

Now, the app can be run, with the database linked in:

```
$ docker run --name myapp-api \
    --link myapp-db:postgres \
    -v $PWD/app:/app \
    -p 8080:80 \
    -e CONNECTION_STRING=postgresql://dbuser:dbpwd@postgres/myapp \
    -e SECRET_KEY=secretkey \
    flask-api
```

### Test

You can create a new account and a corresponding access token using curl:

```
curl -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"john_doe","password":"xyz"}' \
    http://localhost:8080/api/user/register
```

And, to retrieve the username of the newly registered account

```
curl -H "Content-Type: application/json" \
     -H "Authorization: jwt <access_token>" \
    http://localhost:8080/api/user/whoami
```


# Caveat

It is usually cautioned against rolling your own user-login related
functionality but I did it anyway. I wanted something simple and
couldn't find a library that didn't try to do to much.

# Related Resources:

I use these flask extensions:

* https://pythonhosted.org/Flask-JWT/
* https://pypi.python.org/pypi/Flask-Cors

I should add SSL support:

* https://github.com/certbot/certbot

This is a good reference if you're looking at doing something more complicated

* https://pythonhosted.org/Flask-Security/

