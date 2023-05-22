from datetime import datetime, timedelta
from flask import Blueprint, jsonify, render_template, request

from website.database import get_all_notes, requests_per_day_data, get_note, defupdate_note, defdelete_note,defcreate_note

notes = Blueprint('notes', __name__)

@notes.route('/notes', methods=['GET', 'POST'])
def notesindex():
    all_notes = get_all_notes()
    
    return render_template("notes.html", notes= all_notes)

@notes.route('/create_note', methods=['post'])
def create_note():
    data = request.get_json()
    message = str(data["message"])
    starttime = (datetime.strptime(data["starttime"], "%Y-%m-%dT%H:%M")).strftime("%Y-%m-%d %H:%M:%S")
    endtime = (datetime.strptime(data["endtime"], "%Y-%m-%dT%H:%M")).strftime("%Y-%m-%d %H:%M:%S")
    defcreate_note(message,starttime,endtime)
    return {}

@notes.route('/update_note/<int:id>', methods=['post'])
def update_note(id):
    note_data = request.get_json()
    
    # Extract the fields from the note data
    message = note_data.get("message")
    starttime = note_data.get("starttime")
    endtime = note_data.get("endtime")
    
    # Parse the datetime strings to datetime objects
    starttime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    endtime = datetime.strptime(endtime, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    
    # Call the update_note function to update the note in the database
    success = defupdate_note(id, message, starttime, endtime)
    if success:
        return jsonify({"message": "Note updated successfully"})
    else:
        return jsonify({"message": "Failed to update note"})

@notes.route('/delete_note/<int:id>', methods=['DELETE'])
def delete_note(id):
    success = defdelete_note(id)
    
    if success:
        return jsonify({"message": "Note deleted successfully"})
    else:
        return jsonify({"message": "Failed to delete note"})