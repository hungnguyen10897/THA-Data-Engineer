from flask import Flask, render_template, flash, url_for, redirect, jsonify, send_file, abort, Response
from src import app
from datetime import datetime
import redshift_connector

conn = redshift_connector.connect(
   host='hung-redshift-cluster.crdxyumc6dnp.eu-west-1.redshift.amazonaws.com',
   port=5439,
   database='tha',
   user='tha_admin',
   password='WJsXNo1TNw'
)

cursor = conn.cursor()

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
def get_campaign(campaign_id):

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
    
    query = f"""
        SELECT * FROM
            (
                SELECT banner_id FROM revenues WHERE campaign_id = {campaign_id} AND quarter = {quarter} ORDER BY revenue DESC, number_of_clicks DESC LIMIT 10
            )
        ORDER BY RANDOM() LIMIT 1
    """

    cursor.execute(query)
    banner_id = cursor.fetchone()

    if banner_id == []:
        return Response(status=404)
    else:
        return redirect(banner_images_url + f"image_{banner_id[0]}.png", code=302)



