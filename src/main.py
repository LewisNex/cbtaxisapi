from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS

import os

# Init app
app = Flask(__name__)
app.config.from_object(os.environ.get('env') or 'src.config.Development')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

CORS(app)

from src.models import User, Job
from src.routes import api

app.register_blueprint(api)