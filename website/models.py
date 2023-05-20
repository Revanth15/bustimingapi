import sqlalchemy
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

db = sqlalchemy()

class BusStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250))
    Latitude = db.Column(db.Float(250))
    Longitude = db.Column(db.Float(250))
    RoadName = db.Column(db.String(250))

