import collections
import datetime
import functools
import logging
import os
import random

import flask
from flask.ext import cors
import flask_jwt
import sqlalchemy
from sqlalchemy import orm

import table
import users
import util


app = flask.Flask(__name__)
cors.CORS(app)


app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1000)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(util.standardConsoleHandler())

engine = sqlalchemy.create_engine(os.environ['CONNECTION_STRING'])
# TODO: replace this with an alembic script
table.Base.metadata.create_all(engine)
db_session = orm.scoped_session(orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

# this provides an /auth endpoint
jwt = util.configureJWT(app, db_session)


# http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/#declarative
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/user/whoami')
@flask_jwt.jwt_required()
def hello():
    user_id = int(flask_jwt.current_identity)
    user = db_session.query(table.User).get(user_id)
    return flask.jsonify(username=user.username)
                          

@app.route('/user/register', methods=['POST'])
def register():
    data = flask.request.json
    username = data['username']
    password = data['password']
    try:
        identity = users.register(db_session, username, password)
        access_token = jwt.jwt_encode_callback(identity)
        return jwt.auth_response_callback(access_token, identity)
    except users.DuplicateUsername:
        return flask.make_response(
            flask.jsonify({'status': 'error', 'description': 'failed to register'}),
            500
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
