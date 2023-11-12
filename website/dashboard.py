from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import DateTime, ForeignKey, create_engine, Column, Integer, String, Float, func, event, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.orm import sessionmaker
from website.database import get_all_users, get_requests_by_hour_data, get_statistics_data, requests_per_day_data, get_requests_with_users, update_user_details
from website.schemas import UserDetailsUpdate

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET', 'POST'])
# @login_required
def dashboardpage():
    requests = get_requests_with_users()
    users = get_all_users()
    return render_template("dashboard.html", users=users, requests = requests)

@dashboard.route('/requests_per_day_data', methods=['GET'])
def requests_per_day():
    return requests_per_day_data()

@dashboard.route('/requests_per_hour_data', methods=['GET'])
def get_requests_by_hour():
    return get_requests_by_hour_data()

@dashboard.route('/site_statistics_data')
def get_statistics():
    return get_statistics_data()

@dashboard.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    update_data = request.json
    result = update_user_details(user_id, update_data)
    return result