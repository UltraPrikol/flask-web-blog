from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import dotenv_values


config = dotenv_values('.env')

app = Flask(__name__)
app.config['POST_PER_PAGE'] = 3
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

from app import routes, models, errors
