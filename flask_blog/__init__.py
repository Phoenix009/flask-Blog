from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SECRET_KEY'] = 'b205b8fe0c70da0d8a7716a0b40ba811'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from flask_blog import routes
