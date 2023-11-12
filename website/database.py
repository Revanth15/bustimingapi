from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from sqlalchemy import Boolean, DateTime, ForeignKey, MetaData, QueuePool, Table, create_engine, Column, Integer, String, Float, desc, func, event, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker,joinedload

from website.reusables import queryAPI

Base = declarative_base()
load_dotenv()
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

def engine_creation():
    engine = create_engine(
        DB_CONNECTION_STRING,
        connect_args={
            "ssl": {"ssl_ca": "/etc/ssl/cert.pem"},
            'connect_timeout': 120
        },
        poolclass=QueuePool,
        pool_size=100,  
        pool_recycle=600,  
        pool_pre_ping=True
    )
    return engine

def generate_session():
    engine = engine_creation()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

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
    ban = Column(Boolean, default=False)
    notesBan = Column(Boolean, default=False)
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

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    message = Column(String(500))
    status = Column(String(50), default="Inactive")
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    usedCount = Column(Integer, default=0)

engine = engine_creation()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

db = Blueprint('db', __name__)
@db.route('/extractbusstops', methods=['get'])
def extractBusstops():  
    session = generate_session()
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
    session.close()
    return dataList

def get_busstop(id):
    session = generate_session()
    busstop = session.query(BusStop).filter_by(id=id).first()
    session.close()
    return busstop

def get_userById(id):
    session = generate_session()
    user = session.query(User).filter_by(id=id).first()
    session.close()
    return user

def get_userByNameandEmail(name,email):
    session = generate_session()
    user = session.query(User).filter_by(username=name, email=email).first()
    session.close()
    return user

def get_all_users():
    session = generate_session()
    users = session.query(User).all()
    session.close()
    return users

def create_user(name, email, version):
    session = generate_session()
    try:
        new_user = User(id=session.query(func.count(User.id)).scalar() + 1, username=str(name), email=str(email), shortcut_version=version)

        session.add(new_user)
        session.commit()

        return new_user
    except Exception as e:
        session.rollback()
        print("Error creating user:", str(e))
        return None
    finally:
        session.close()

if session.query(User).count() == 0:
    create_user("default","default@gmail.com","v1")


session.close()

def update_userDetails(id,sh_version):
    session = generate_session()
    user = get_userById(id)
    try:
        user = session.merge(user)
        dt = datetime.now(timezone.utc).date()
        if user.last_used:
            if dt > user.last_used.date():
                user.days_active += 1
        else:
            user.days_active += 1
        user.num_requests += 1
        user.last_used = datetime.utcnow() + timedelta(hours=8)
        user.shortcut_version = sh_version
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()

    finally:
        session.close()

def update_user_details(user_id: int, update_data: dict):
    session = generate_session()
    user = get_userById(user_id)
    try:
        user = session.merge(user)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.ban = update_data.get("ban")
        user.notesBan = update_data.get("notesban")
        session.commit()
        return {"message": "User details updated successfully"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user details: {e}")
    finally:
        session.close()

def create_request(bus_stop_code, options, user_id, requested_buses, sh_version):
    session = generate_session()
    try:
        request = Request(id=session.query(func.count(Request.id)).scalar() + 1, bus_stop_code=bus_stop_code, options=options, timestamp=datetime.utcnow() + timedelta(hours=8), user_id=user_id)
        session.add(request)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error creating request:", str(e))
        return False

    requested_buses_list = []
    val = 1
    for bus in requested_buses:
        if bus == "null":
            bus = "All Buses"
        requested_bus = RequestedBuses(id=session.query(func.count(RequestedBuses.id)).scalar() + val, bus_number=bus, request_id=request.id)
        requested_buses_list.append(requested_bus)
        val += 1
    update_userDetails(user_id,sh_version)
    try:
        session.add_all(requested_buses_list)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error creating requested buses:", str(e))
        return False
    finally:
        session.close()

def get_all_notes():
    session = generate_session()
    notes = session.query(Note).all()
    session.close()
    return notes

def defcreate_note(message, starttime, endtime):
    session = generate_session()
    note = Note(id=session.query(func.count(Note.id)).scalar() + 1, message=message, starttime=starttime, endtime=endtime)
    session.add(note)
    session.commit()
    session.close()

def get_note(note_id):
    session = generate_session()
    note = session.query(Note).get(note_id)
    session.close()
    return note

def defupdate_note(note_id, message=None, starttime=None, endtime=None):
    session = generate_session()
    note = session.query(Note).get(note_id)
    if note is None:
        session.close()
        return False

    if message:
        note.message = message
    if starttime:
        note.starttime = starttime
    if endtime:
        note.endtime = endtime

    session.commit()
    session.close()
    return True

def defdelete_note(note_id):
    session = generate_session()
    note = session.query(Note).get(note_id)
    if note is None:
        session.close()
        return False
    print(note.id)
    session.delete(note)
    session.commit()
    session.close()
    return True

def increment_used_count(note_id):
    session = generate_session()
    note = session.query(Note).get(note_id)
    if note is None:
        session.close()
        return False

    note.usedCount += 1
    session.commit()
    session.close()
    return True

def get_note_message(user):
    session = generate_session()
    current_time = datetime.now().astimezone(timezone(timedelta(hours=8)))

    notes = get_all_notes()
    if(user.notesBan == False):
        for note in notes:
            note_start = note.starttime.astimezone(timezone(timedelta(hours=8)))
            note_end = note.endtime.astimezone(timezone(timedelta(hours=8)))
            if note_start <= current_time <= note_end:
                print("true")
                if note.status == "Inactive" or note.status == "Ongoing":
                    print("true1")
                    # if current_time > note.endtime:
                    #     print("true2")
                    #     note.status = "Finished"
                    if note.status == "Inactive":
                        print("true3")
                        note.status = "Ongoing"
                    increment_used_count(note.id)
                    session.commit()
                    session.close()
                    return note.message

    session.close()
    return None

def requests_per_day_data():
    session = generate_session()
    result = session.query(func.date(Request.timestamp).label('date'), func.count(Request.id).label('count')).group_by(func.date(Request.timestamp)).all()
    requests_data = []
    for row in result:
        request_date = row.date.strftime('%Y-%m-%d')
        requests_count = row.count
        requests_data.append({'date': request_date, 'count': requests_count})
    session.close()
    return jsonify(requests_data)

def get_requests_by_hour_data():
    session = generate_session()

    sg_timezone = timezone(timedelta(hours=8))

    now = datetime.now()
    start_time = now - timedelta(hours=24)
    start_time_sg = start_time.replace(tzinfo=sg_timezone)

    result = session.query(
        func.date_format(Request.timestamp, '%Y-%m-%d %H:00:00').label('hour'),
        func.count(Request.id).label('count')
    ).filter(Request.timestamp >= start_time_sg).group_by('hour').order_by('hour').all()

    data = [{'hour': row.hour, 'count': row.count} for row in result]
    session.close()
    return jsonify(data)


def get_statistics_data():
    session = generate_session()
    # Total requests
    total_requests = session.query(func.count(Request.id)).scalar()

    # Most requested bus stops
    most_requested_stops = session.query(Request.bus_stop_code, func.count(Request.id)).\
        filter(Request.bus_stop_code != 'All Busses').\
        group_by(Request.bus_stop_code).\
        order_by(func.count(Request.id).desc()).all()

    # Bus numbers count
    bus_numbers_count = session.query(RequestedBuses.bus_number, func.count(RequestedBuses.bus_number)).\
        filter(RequestedBuses.bus_number != 'All Busses').\
        group_by(RequestedBuses.bus_number).all()

    data = {
        'total_requests': total_requests,
        'most_requested_stops': [{'bus_stop_code': stop_code, 'count': count} for stop_code, count in most_requested_stops],
        'bus_numbers_count': [{'bus_number': bus_number, 'count': count} for bus_number, count in bus_numbers_count]
    }
    session.close()
    return jsonify(data)

def get_requests_with_users():
    session = generate_session()
    requests_users = session.query(Request).\
                    join(User).\
                    options(joinedload(Request.user)).\
                    order_by(desc(Request.timestamp)).\
                    all()
    return requests_users