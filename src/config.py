import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = '42'
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

class Production(Config):
    TESTING = False
    DEBUG = False
    DEVELOPMENT = False

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL')

    


