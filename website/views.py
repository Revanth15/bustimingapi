from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import requests
from datetime import datetime, timedelta, timezone
# from . import db
import json
import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_KEY = os.getenv('ACCOUNT_KEY')
views = Blueprint('views', __name__)

env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
views.config.from_object(env_config)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

    return render_template("home.html", user=current_user)


@views.route('/bustiming/<int:busstopcode>/<string:busno>', methods=['get'])
def get_bustiming(busstopcode,busno):  

    test = {
        "Services": [
            {
            "BusNo": "858", 
            "estArrivalTime": "3 mins"
            }, 
            {
            "BusNo": "883", 
            "estArrivalTime": "2 mins"
            }, 
            {
            "BusNo": "969", 
            "estArrivalTime": "arriving (lastbus)"
            }
        ]   
    }
    data = {}
    list = []
    # print(busstopcode)
    if busno != 'null':
        buslist = busno.split(',')
    # print(buslist)
    url = f"http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}"
    headers = {
    'AccountKey': ACCOUNT_KEY
    }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    services = response['Services']
    if busno != 'test':
        for i in services:
            if i['ServiceNo'] in buslist:
                
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
                print(f"{i['ServiceNo']} : {arrivaltime} ")
                list.append({'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime })
        data['Services'] = list
    else:
        data = test
    # response = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}}')
    # print(json.dumps(services,indent=1))
    print(data)
    return jsonify(data)