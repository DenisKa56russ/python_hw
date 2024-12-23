from .accounts.routers import account_routers
from flask import Flask

app = Flask(__name__)
app.register_blueprint(account_routers)