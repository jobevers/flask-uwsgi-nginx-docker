import collections
import datetime
import functools
import logging
import sys

import flask
import flask_jwt

import users


def standardConsoleHandler():
    result = logging.StreamHandler(sys.stdout)
    format_ = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    formatter = logging.Formatter(format_)
    result.setFormatter(formatter)
    return result


def configureJWT(app, db_session):
    jwt = flask_jwt.JWT(app, functools.partial(users.authenticate, db_session), users.identity)
    # this is nearly identical to the default except that
    # they use the `id` property and I use the `id_` property
    def jwt_payload_handler(user):
        iat = datetime.datetime.utcnow()
        exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
        return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': user.id_}
    jwt.jwt_payload_handler(jwt_payload_handler)
    return jwt
