from flask import Flask, render_template, flash, url_for, redirect, jsonify, send_file, abort, Response, request
from src import app
from datetime import datetime
from pathlib import Path

from src.backend import get_banner_id, upload_csv

banner_images_url = "https://hungthas3.s3.eu-west-1.amazonaws.com/banner_images/"

@app.route("/campaigns",  methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/campaigns/<campaign_id>", methods= ["GET"])
def get_banner(campaign_id):

    # Test path parameter, avoid SQL Injection
    try:    
        campaign_id = int(campaign_id)
    except ValueError:
        return Response("Invalid Campaign ID", status=404)

    request_time = datetime.now()
    if 0 <= request_time.minute < 15:
        quarter = 1
    elif 15 <= request_time.minute < 30:
        quarter = 2
    elif 30 <= request_time.minute < 45:
        quarter = 3
    else:
        quarter = 4
    
    banner_id = get_banner_id(campaign_id, quarter)
    if banner_id is None:
        return Response(status=404)
    else:
        return redirect(banner_images_url + f"image_{banner_id}.png", code=302)


@app.route("/campaigns", methods = ["POST"])
def upload():

    table = request.form.get("table")
    quarter = request.form.get("quarter")
    uploaded_file = request.files['file']

    file_parts = uploaded_file.filename.split('.')
    if len(file_parts) != 2:
        return "Invalid Name for CSV file", 400

    file_type = file_parts[-1]
    if file_type != 'csv':
        return "File should  be of type CSV", 400
    
    parent_path = Path(app.config['UPLOAD_FOLDER'])
    parent_path.mkdir(parents=True, exist_ok=True)
    file_path = parent_path.joinpath(uploaded_file.filename)

    uploaded_file.save(file_path)
    
    succeeded, msg = upload_csv(file_path, table, quarter)

    file_path.unlink()

    if succeeded:
        print(f"Successfully uploaded to table '{table}' for quarter '{quarter}'")
        return redirect(url_for('index'))
    else:
        return msg, 400

