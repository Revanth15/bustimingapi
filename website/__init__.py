from flask import Flask
from os import path
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

def create_app():
    app = Flask(__name__)

    from .views import views
    from .dbs import dbs
    from .database import db

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(dbs, url_prefix='/')
    app.register_blueprint(db, url_prefix='/')

    # from .db.models import BusStop

    return app

