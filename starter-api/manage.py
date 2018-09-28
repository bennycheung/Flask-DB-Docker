#!/usr/bin/env python
import json
import logging
import logging.config
import os

from api.app import create_app
from api.models import (
    db,
    User,
)
from flask.ext.script import (
    Manager,
)

# Setup logging configuration
logging_config = json.load(open('configuration/logging.json', 'r'))
logging.config.dictConfig(logging_config)


# Flask manager scripting
manager = Manager(create_app(os.getenv('FLASK_CONFIG') or 'default'))


@manager.command
def createdb():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        db.drop_all()
        db.create_all()


@manager.command
def adduser(username):
    """Register a new user."""
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


@manager.command
def adduserpass(username, password):
    """Register a new user with password"""
    db.create_all()
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


@manager.command
def test():
    from subprocess import call
    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=api', '--cover-package=orderbook',
          '--cover-branches', '--cover-erase', '--cover-html',
          '--cover-html-dir=test_results/coverage'])
    #       '--exclude-dir=tasks'])


if __name__ == '__main__':
    manager.run()
