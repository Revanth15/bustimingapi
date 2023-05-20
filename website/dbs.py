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
from website.reusables import queryAPI

dbs = Blueprint('dbs', __name__)

@dbs.route('/healthcheckdbs', methods=['get'])
def healthcheckdbs():  
    user_ip = request.remote_addr
    print(user_ip)
    response = "Healthy"
    return response