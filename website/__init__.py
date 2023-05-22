from flask import Flask
from os import path
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    from .views import views
    from .dbs import dbs
    from .database import db
    from .dashboard import dashboard
    from .note import notes

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(dbs, url_prefix='/')
    app.register_blueprint(db, url_prefix='/')
    app.register_blueprint(dashboard, url_prefix='/admin')
    app.register_blueprint(notes, url_prefix='/admin')

    return app

