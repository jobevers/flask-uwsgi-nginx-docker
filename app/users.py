import hashlib
import logging
import random
import string

import sqlalchemy

import table


logger = logging.getLogger(__name__)


class DuplicateUsername(Exception):
    pass


def _randomString(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def _hash(salt, password):
    return hashlib.sha256(salt + password).hexdigest()


def register(db_session, username, password):
    salt = _randomString()
    password_hash = _hash(salt, password)
    user = table.User(username=username, password_hash=password_hash, password_salt=salt)
    db_session.add(user)
    try:
        db_session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise DuplicateUsername('username {} already exists'.format(username))
    return user


def authenticate(db_session, username, password):
    try:
        user = db_session.query(table.User).filter(table.User.username == username).one()
    except sqlalchemy.orm.exc.NoResultFound:
        logging.info('Authenticate failed: user %s does not exist', username)
        return None
    password_hash = _hash(user.password_salt, password)
    # TODO: should use a string comparision that takes the same amount of time
    #       regardless of success or failure
    if password_hash != user.password_hash:
        logging.info('Authenticate failed: invalid password')
        return None
    return user


def identity(payload):
    return payload['identity']


