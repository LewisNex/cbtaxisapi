from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail

import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['ADMIN_EMAIL'] = os.environ.get("ADMIN_EMAIL")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
print('USING DATABASE: ' + os.environ.get('DATABASE_URL'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['ENV'] = os.environ.get('ENV', default='DEV')
app.config['DEV'] = app.config['ENV'] == 'DEV'
# app.config['DEV'] = app.config['ENV'] == False

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

from src.models import User, Job
from src.routes import api

app.register_blueprint(api)
