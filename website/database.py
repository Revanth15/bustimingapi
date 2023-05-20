from dotenv import load_dotenv
from flask import Blueprint
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker

from website.reusables import queryAPI

Base = declarative_base()
load_dotenv()
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
engine = create_engine(
    DB_CONNECTION_STRING,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem" 
                }
    })

class BusStop(Base):
    __tablename__ = 'busstop'
    id = Column(String(5), primary_key=True)
    description = Column(String(250))
    Latitude = Column(Float)
    Longitude = Column(Float)
    RoadName = Column(String(250))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# session.close()

db = Blueprint('db', __name__)
@db.route('/extractbusstops', methods=['get'])
def extractBusstops():  
    counter = 0
    dataList = []
    flatten = lambda l: [y for x in l for y in x]
    busstops = session.query(BusStop).first()
    if busstops is None:
        while True:  
            res = queryAPI("ltaodataservice/BusStops",{"$skip" : str(counter)})
            if len(res["value"]) == 0:
                break
            else:
                dataList.append(res["value"])
                counter+=500
        dataList = flatten(dataList)
        for stop in dataList:
            new_busstop = BusStop(id=stop['BusStopCode'], description=stop['Description'], Latitude=stop['Latitude'], Longitude=stop['Longitude'], RoadName=stop['RoadName'])
            session.add(new_busstop)
        session.commit()
    else:
        dataList = ["Stops already extracted"]
    return dataList

def get_busstop(id):
    return session.query(BusStop).filter_by(id=id).first()
