from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import requests
from datetime import datetime, timedelta, timezone
# from . import db
import json
import os
from dotenv import load_dotenv

from website.database import get_busstop, get_userById, get_userByNameandEmail, create_user, update_userDetails, create_request

load_dotenv()
deployed = False
ACCOUNT_KEY = os.getenv('ACCOUNT_KEY')
views = Blueprint('views', __name__)

# env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
# views.config.from_object(env_config)

@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

    return render_template("home.html", user=current_user)

@views.route('/bustiming/<int:busstopcode>/<string:busno>/<string:options>', methods=['get'])
def get_bustiming(busstopcode,busno,options):  
    global deployed
    test = {
        "Services": [
            {
                "BusNo": "117",
                "estArrivalTime": "8 mins",
                "options": "Seats Available | WheelChair"
            },
            {
                "BusNo": "169",
                "estArrivalTime": "2 mins",
                "options": "Seats Available | WheelChair"
            }
        ],
        "stopName": "Yishun Stn"
    }
    data = {}
    list = []
    user = None
    optionsList = options.split(',')
    if(request.headers.get('Details') is not None and request.headers.get('Email') is not None):
        user = get_userByNameandEmail(request.headers.get('Details'),request.headers.get('Email'))
        if user is None:
            user = create_user(request.headers.get('Details'),request.headers.get('Email'))
    else:
        user = get_userById(1)

    print(user.username)
    host = request.host  # identify host
    if deployed == False:
        if host.startswith('localhost') or host.startswith('127.0.0.1'):
            print('Request from localhost')
        else:
            deployed = True
            print('Using the server!')
    buslist = busno.split(',')
    buslist = [i for i in buslist if i]
    if len(buslist) > 1:
        if buslist[0] == 'null':
            buslist.remove('null')
    url = f"http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}"
    headers = {
    'AccountKey': ACCOUNT_KEY
    }
    create_request(busstopcode,options,user.id,buslist)
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    services = response['Services']
    if busno == "null" or buslist[0] == 'null':
        for i in services:
            list.append(getArrivingTime(i, optionsList))
        data['Services'] = list
        data['stopName'] = get_busstop(str(busstopcode)).description
        print(f"Data for all busses @ {busstopcode} sent")
    elif busno != 'test' or buslist[0] != 'null':
        for i in services:
            if i['ServiceNo'] in buslist:
                list.append(getArrivingTime(i, optionsList))
        data['Services'] = list
        data['stopName'] = get_busstop(str(busstopcode)).description
        print(f"Data for {buslist} @ {busstopcode} buss(es) sent")
    else:
        data = test
    return jsonify(data)

def checkOptions(service,optionsList):
    optionsDict = {
        0 : "Load",
        1 : "Feature",
        2 : "Type",
        "Load" : {
            "SEA": "Seats Available",
            "SDA": "Standing",
            "LSD": "Limited Standing"
        },
        "Feature" : {
            "WAB" : "WheelChair"
        },
        "Type" : {
            "SD": "Single",
            "DD": "Double Deck",
            "BD": "Bendy"
        },
    }
    optionString= ""
    opList = []
    for i in range(len(optionsList)):
        if optionsList[i].upper() == "YES" or optionsList[i].upper() == "TRUE":
            val = service['NextBus'][str(optionsDict[i])]
            # print(optionsDict[str(optionsDict[i])])
            opList.append(optionsDict[str(optionsDict[i])][val])
            optionString = ' | '.join([str(x) for x in opList])
    return optionString

def getArrivingTime(i, optionsList):
    op = checkOptions(i,optionsList)
    now = datetime.now(timezone.utc)
    if i['NextBus']['EstimatedArrival'] != '':
        arrivaltime = int((datetime.fromisoformat(i['NextBus']['EstimatedArrival']).replace(tzinfo=timezone(timedelta(hours=8))) - now).total_seconds() // 60)
        # nextbus = int((datetime.fromisoformat(i['NextBus2']['EstimatedArrival']).replace(tzinfo=timezone(timedelta(hours=8))) - now).total_seconds() // 60)
        lastbus = ""
        if i['NextBus2']['EstimatedArrival'] == '':
            lastbus = " (lastbus)"
        if arrivaltime <= 0:
            arrivaltime = f"arriving{lastbus}"
        elif arrivaltime == 1:
            arrivaltime = f'1 min{lastbus}'
        else:
            arrivaltime = f"{arrivaltime} mins{lastbus}"
    else:
        arrivaltime = "not operating right now"
    # print(f"{i['ServiceNo']} : {arrivaltime} ")
    return {'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime, 'options' : op}

@views.route('/healthcheck', methods=['get'])
def healthcheck():  

    response = "Healthy"
    return response