from flask import Flask
from flask_swagger_ui import flask_swagger_ui, get_swaggerui_blueprint
import Routs
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, and_
from flask import Flask, request, jsonify, json, make_response
from flask_marshmallow import Marshmallow
from Models import *

app = Flask(__name__) 
ma = Marshmallow(app)

# BLUEPRINTS
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL,
                                            config={'app_name': 'LPNU students'})
app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)

app.register_blueprint(Routs.student)
app.register_blueprint(Routs.teacher)

# SQLALCHEMY
engine = create_engine("mysql+pymysql://root:1234@127.0.0.1:3307/lab", echo=True)
session = sessionmaker(bind=engine)
s = session()

if __name__ == "__main__":
    app.run()
