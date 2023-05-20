import os
from dotenv import load_dotenv
import requests

load_dotenv()
ACCOUNT_KEY = os.getenv('ACCOUNT_KEY')

def queryAPI(path, params):
    url = "http://datamall2.mytransport.sg/"
    headers = {
    'AccountKey': ACCOUNT_KEY
    }
    return requests.get(url + path, headers=headers,params=params).json()