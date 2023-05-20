from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Blueprint
from sqlalchemy import DateTime, ForeignKey, create_engine, Column, Integer, String, Float, func, event
from sqlalchemy.orm import relationship
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

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(75))
    num_requests = Column(Integer, default=0)
    last_used = Column(DateTime)
    days_active = Column(Integer, default=0)
    shortcut_version = Column(String(10))
    requests = relationship('Request', back_populates='user')

class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True)
    bus_stop_code = Column(String(10), nullable=False)
    options = Column(String(250), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow() + timedelta(hours=8))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='requests')
    requested_busses = relationship('RequestedBuses', back_populates='request')

class RequestedBuses(Base):
    __tablename__ = 'requested_buses'

    id = Column(Integer, primary_key=True)
    bus_number = Column(String(20), nullable=False)
    request_id = Column(Integer, ForeignKey('requests.id'), nullable=False)
    request = relationship('Request', back_populates='requested_busses')

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

def get_userById(id):
    return session.query(User).filter_by(id=id).first()

def get_userByNameandEmail(name,email):
    return session.query(User).filter_by(username=name, email=email).first()

def create_user(name, email,version):
    try:
        new_user = User(id=session.query(func.count(User.id)).scalar() + 1, username=str(name), email=str(email),shortcut_version=version)

        session.add(new_user)
        session.commit()

        return new_user
    except Exception as e:
        session.rollback()
        print("Error creating user:", str(e))
        return None

def update_userDetails(id):
    user = get_userById(id)
    dt = (datetime.now() + timedelta(hours=8)).date()
    if user.last_used:
        if dt > user.last_used.date():
            user.days_active += 1
    else:
        user.days_active += 1
    user.num_requests += 1
    user.last_used = datetime.utcnow() + timedelta(hours=8)
    session.commit()

def create_request(bus_stop_code, options, user_id, requested_buses):
    try:
        request = Request(id=session.query(func.count(Request.id)).scalar() + 1,bus_stop_code=bus_stop_code, options=options, timestamp=datetime.utcnow() + timedelta(hours=8), user_id=user_id)
        session.add(request)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error creating request:", str(e))
    requested_buses_list = []
    val = 1
    for bus in requested_buses:
        if bus != "null":
            requested_bus = RequestedBuses(id=session.query(func.count(RequestedBuses.id)).scalar() + val, bus_number=bus, request_id=request.id)
            requested_buses_list.append(requested_bus)
            val += 1
    update_userDetails(user_id)
    try:
        # Add the request and requested buses to the session and commit the changes
        session.add_all(requested_buses_list)
        session.commit()
        return True
    except Exception as e:
        # Handle any errors that occurred during the database operation
        session.rollback()
        print("Error creating requestedbusses:", str(e))
        return False
    
if session.query(User).count() == 0:
    create_user("default","default@gmail.com","v1")