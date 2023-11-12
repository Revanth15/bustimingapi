
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

# from datetime import datetime, timedelta

# from website.database import get_userById
# print(datetime.utcnow() + timedelta(hours=8))

# import os

# import os

# def get_folder_size(folder_path):
#     total_size = 0
#     for path, dirs, files in os.walk(folder_path):
#         for f in files:
#             fp = os.path.join(path, f)
#             try:
#                 total_size += os.path.getsize(fp)
#             except FileNotFoundError:
#                 print(f"File not found: {fp}")
#     return total_size / (1024**3)  # Convert to GB

# def list_folders_with_size(drive_path):
#     folder_list = []
#     for folder_name in os.listdir(drive_path):
#         folder_path = os.path.join(drive_path, folder_name)
#         if os.path.isdir(folder_path):
#             try:
#                 folder_size = get_folder_size(folder_path)
#                 folder_list.append((folder_name, folder_size))
#             except FileNotFoundError:
#                 print(f"Folder not found: {folder_path}")
#     return folder_list

# # Usage example
# drive_path = 'C:\\Users\\revan\\Pictures\\'
# folders = list_folders_with_size(drive_path)
# for folder_name, folder_size in folders:
#     print(f"Folder: {folder_name}\tSize: {folder_size:.2f} GB")

from PIL import Image, ImageDraw, ImageFont

# Data from API
data = [
    {"bus_number": 117, "arrival_time": 18, "seats_available": "Seats Available"},
    {"bus_number": 169, "arrival_time": 7, "seats_available": "Seats Available"},
    {"bus_number": 858, "arrival_time": 9, "seats_available": "Seats Available"},
    {"bus_number": 883, "arrival_time": 22, "seats_available": "Seats Available"},
    {"bus_number": 965, "arrival_time": 31, "seats_available": "Seats Available"},
    {"bus_number": 969, "arrival_time": 18, "seats_available": "Seats Available"},
]

# Create an image
image = Image.new("RGB", (400, 200), "white")
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Draw text on the image
draw.text((10, 10), "Yishun Stn", fill="black", font=font)

y_position = 40
for item in data:
    text = f"{item['bus_number']} : {item['arrival_time']} mins | {item['seats_available']}"
    draw.text((10, y_position), text, fill="black", font=font)
    y_position += 20

# Save the image
image.save("bus_schedule.png")