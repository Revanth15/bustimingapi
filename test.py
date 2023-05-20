
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




# @dbs.route('/busstop/<int:busstopcode>', methods=['get'])
# def get_busstops(busstopcode):  

#     counter = 0
#     bsList = [] #bus stop list
#     dataList = [] # information about each bus stop
#     flatten = lambda l: [y for x in l for y in x]
    
#     while True:  
#         res = queryAPI("ltaodataservice/BusStops",{"$skip" : str(counter)})
#         if len(res["value"]) == 0:
#             break
#         else:
#             bsList.append([x["BusStopCode"] for x in res["value"]])
#             dataList.append(res["value"])
#             counter+=500
            
#     bsList = flatten(bsList)
#     dataList = flatten(dataList)
#     return dict(zip(bsList,dataList))

from datetime import datetime, timedelta

from website.database import get_userById
print(datetime.utcnow() + timedelta(hours=8))