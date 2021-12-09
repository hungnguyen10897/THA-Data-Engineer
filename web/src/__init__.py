from flask import Flask, render_template, flash, url_for, redirect
import json

# with open("./src/config.json", "r") as f:
#     config = json.load(f)

app = Flask(__name__)
# app.config['SECRET_KEY'] = config["SECRET_KEY"]
# app.config['SQLALCHEMY_DATABASE_URI'] = config["SQLALCHEMY_DATABASE_URI"]
# db = SQLAlchemy(app)
# engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

from src import routes
