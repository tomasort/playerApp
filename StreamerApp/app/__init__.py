from flask import Flask, render_template
import json
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from celery import Celery, Task
from config import config
from app.streaming import GstreamerPipeline
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
moment = Moment()
socketio = SocketIO()
mail = Mail()
bootstrap = Bootstrap()

buttons = set(json.load(open('./app/static/buttons.json')))

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/myapp.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.info('MyApp startup')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    # set up Celery
    celery_init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    setup_logging(app)
    app.logger.info('The App has been created!')

    return app
