from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '5791628bb0b13ce0c676dfde280ba245')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


from latte_gallery.accounts import routes
from latte_gallery.core import routes