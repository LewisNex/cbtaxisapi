from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail

import os

from environs import Env
env = Env()
env.read_env()

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = env.str('SECRET_KEY')
app.config['ADMIN_EMAIL'] = env.str("ADMIN_EMAIL")

app.config['SQLALCHEMY_DATABASE_URI'] = env.str('DATABASE_URI', default='sqlite:///' + os.path.join(basedir, 'db.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['ENV'] = env.str('ENV', default='DEV')
app.config['DEV'] = app.config['ENV'] == 'DEV'
# app.config['DEV'] = app.config['ENV'] == False

app.config['MAIL_SERVER'] = env.str('MAIL_SERVER')
app.config['MAIL_PORT'] = env.str('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = env.str('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = env.str('MAIL_PASSWORD')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

from src.models import User, Job
from src.routes import api

app.register_blueprint(api)
