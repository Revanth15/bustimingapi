import threading
import time
import schedule
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import requests
from datetime import datetime, timedelta, timezone
# from . import db
import json
import os
from dotenv import load_dotenv

load_dotenv()
scheduler_running = False
deployed = False
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

# def job():
#     # url = "https://timesaver-suam.onrender.com/bustiming/59079/null/True,True,False"
#     # response = requests.request("GET", url)
#     print("Hellow")

# def start_scheduler():
#     global scheduler_running
#     scheduler_running = True
#     schedule.every(8).minutes.do(job)

#     while scheduler_running:
#         schedule.run_pending()
#         time.sleep(1)

# def stop_scheduler():
#     global scheduler_running
#     scheduler_running = False

# @views.before_request
# def before_request():
#     global deployed
#     if deployed == True:
#         # Stop the scheduler when a request is received
#         if scheduler_running:
#             stop_scheduler()
#             print("Ending Scheduler") 

# @views.after_request
# def after_request(response):
#     global deployed
#     global scheduler_running
#     if deployed == True:
#         if not scheduler_running:
#             threading.Thread(target=start_scheduler).start()
#             print("Starting Scheduler")
#             print(scheduler_running)
#         return response

# if deployed == True:
#     print('yellow')
#     @views.before_request
#     def before_request():

#         # Stop the scheduler when a request is received
#         if scheduler_running:
#             stop_scheduler()

#         print("before")

#     @views.after_request
#     def after_request(response):

#         if not scheduler_running:
#             threading.Thread(target=start_scheduler).start()
#         print("response")
#         return response

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
            },
            {
                "BusNo": "858",
                "estArrivalTime": "1 min",
                "options": "Seats Available | WheelChair"
            },
            {
                "BusNo": "883",
                "estArrivalTime": "9 mins",
                "options": "Seats Available | WheelChair"
            },
            {
                "BusNo": "965",
                "estArrivalTime": "1 min",
                "options": "Seats Available | WheelChair"
            },
            {
                "BusNo": "969",
                "estArrivalTime": "arriving",
                "options": "Seats Available | WheelChair"
            }
        ]
    }
    data = {}
    list = []
    optionsList = options.split(',')

    # identify host
    host = request.host
    # print(host)
    if deployed == False:
        if host.startswith('localhost') or host.startswith('127.0.0.1'):
            print('Request from localhost')
        else:
            deployed = True
            print('Using the server!')
    # print(deployed)
    buslist = busno.split(',')
    buslist = [i for i in buslist if i]
    if len(buslist) > 1:
        if buslist[0] == 'null':
            buslist.remove('null')
    # print(buslist)
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
            # print(f"{i['ServiceNo']} : {arrivaltime} ")
            list.append({'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime , 'options' : op})
        data['Services'] = list
        print(f"Data for all busses @ {busstopcode} sent")
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
                # print(f"{i['ServiceNo']} : {arrivaltime} ")
                list.append({'BusNo': i['ServiceNo'], 'estArrivalTime' : arrivaltime, 'options' : op})
        data['Services'] = list
        print(f"Data for {buslist} @ {busstopcode} buss(es) sent")
    else:
        data = test
    # response = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={busstopcode}}')
    # print(json.dumps(services,indent=1))
    # print(data)
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
        if optionsList[i].upper() == "YES" or optionsList[i].upper() == "TRUE":
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

@views.route('/healthcheck', methods=['get'])
def healthcheck():  

    response = "Healthy"
    return response