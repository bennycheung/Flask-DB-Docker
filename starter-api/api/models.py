from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import (
    current_app,
    url_for,
)
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from .helpers import args_from_url
from .errors import ValidationError

db = SQLAlchemy()


class PxCode(db.Model):
    __tablename__ = 'starter_pxcodes'

    id = db.Column(db.Integer, primary_key=True)
    pxcode = db.Column(db.String(10), nullable=False, unique=True, index=True)
    procedure = db.Column(db.String(80))

    def get_url(self):
        return url_for('api.get_pxcode', pxcode=self.pxcode, _external=True)

    def to_json(self):
        return {
            'url': self.get_url(),
            'pxcode': self.pxcode,
            'procedure': self.procedure
        }

    def from_json(self, json):
        try:
            self.pxcode = json['pxcode']
        except KeyError as e:
            raise ValidationError('Invalid pxcode: missing ' + e.args[0])

        try:
            self.procedure = json['procedure']
        except KeyError as e:
            raise ValidationError('Invalid pxcode: missing ' + e.args[0])

        return self

class User(db.Model):
    __tablename__ = 'starter_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    image = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])
