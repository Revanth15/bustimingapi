from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template
from sqlalchemy import DateTime, ForeignKey, create_engine, Column, Integer, String, Float, func, event, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker

from website.database import get_requests_by_hour_data, get_statistics_data, requests_per_day_data, get_requests_with_users

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET', 'POST'])
# @login_required
def dashboardpage():
    requests = get_requests_with_users()
    # for request in requests:
    #     print("Request ID:", request.id)
    #     print("User:", request.user.username)
    #     print("Timestamp:", request.timestamp)
    return render_template("dashboard.html", requests = requests)

@dashboard.route('/requests_per_day_data', methods=['GET'])
def requests_per_day():
    return requests_per_day_data()

@dashboard.route('/requests_per_hour_data', methods=['GET'])
def get_requests_by_hour():
    return get_requests_by_hour_data()

@dashboard.route('/site_statistics_data')
def get_statistics():
    return get_statistics_data()