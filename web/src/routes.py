from flask import Flask, render_template, flash, url_for, redirect, jsonify, send_file, abort, Response
from src import app
from datetime import datetime

from backend import get_banner_id
from web.src.backend import get_banner_id 


banner_images_url = "https://hungthas3.s3.eu-west-1.amazonaws.com/banner_images/"

@app.route("/campaigns",  methods=['GET'])
def index():

    # projects = get_projects(organization)
    # project_array = []
    # for name in projects:
    #     project_obj = {}
    #     project_obj["name"] = name
    #     project_array.append(project_obj)
    
    return jsonify({"projects" : "THA"})

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


@app.route("", methods = ["POST"])
def upload():
    pass
