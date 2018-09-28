import logging

from flask import Flask

from .models import db
from config import config

logger = logging.getLogger(__name__)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    logger.debug("app configuration %s" % (str(app.config)))

    db.init_app(app)

    from api.v1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    if app.config['USE_TOKEN_AUTH']:
        from api.token import token as token_blueprint
        app.register_blueprint(token_blueprint, url_prefix='/auth')
    return app
