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

# env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
# views.config.from_object(env_config)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

    return render_template("home.html", user=current_user)


@views.route('/bustiming/<int:busstopcode>/<string:busno>/<string:options>', methods=['get'])
def get_bustiming(busstopcode,busno,options):  

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
    optionsList = options.split(',')
    print(optionsList)
    # print(busstopcode)
    # if busno != 'null':
    buslist = busno.split(',')
    buslist = [i for i in buslist if i]
    if len(buslist) > 1:
        if buslist[0] == 'null':
            buslist.remove('null')
    print(buslist)
    url = f"http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}"
    headers = {
    'AccountKey': ACCOUNT_KEY
    }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    services = response['Services']
    if busno == "null" or buslist[0] == 'null':
        for i in services:
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
            print(f"{i['ServiceNo']} : {arrivaltime} ")
            list.append({'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime , 'options' : options})
        data['Services'] = list
    elif busno != 'test' or buslist[0] != 'null':
        for i in services:
            if i['ServiceNo'] in buslist:
                
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
                print(f"{i['ServiceNo']} : {arrivaltime} ")
                list.append({'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime, 'options' : op})
        data['Services'] = list
    else:
        data = test
    # response = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}}')
    # print(json.dumps(services,indent=1))
    print(data)
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
    # for option in optionsList:
    #     if option == "False":
    #         print(option)
    for i in range(len(optionsList)):
        if optionsList[i] == "True":
            val = service['NextBus'][str(optionsDict[i])]
            # print(optionsDict[str(optionsDict[i])])
            opList.append(optionsDict[str(optionsDict[i])][val])
            optionString = ' | '.join([str(x) for x in opList])
    return optionString

@views.route('/busstop/<int:busstopcode>', methods=['get'])
def get_busstop(busstopcode):  

    url = f"http://datamall2.mytransport.sg/ltaodataservice/BusStops"
    headers = {
    'AccountKey': ACCOUNT_KEY
    }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    print(response)
    services = response['value']
    
    return jsonify(services)