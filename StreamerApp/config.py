import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'This string is an extreamly hard to guess')
    VIDEO_SOURCE = os.environ.get('VIDEO_SOURCE', None)
    AUDIO_SOURCE = os.environ.get('AUDIO_SOURCE', None)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', "example@gmail.com")
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp-relay.sendinblue.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[PlayerApp]'
    MAIL_SENDER = 'PlayerApp Admin <example@gmail.com>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SSL_REDIRECT = False
    WEBRTC_URI = os.environ.get('WEBRTC_URI', "ws://127.0.0.1:8443")
    CELERY=dict(
        broker_url=os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
        result_backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"),
        task_ignore_result=True,
    )

    @staticmethod
    def init_app(app):
        pass


# TODO: create a database for dev and for test in postgres
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
