from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_rq2 import RQ

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
api = Api(app)
cors = CORS(app, supports_credentials=True)
rq = RQ(app)
from icecream import ic

ic()

worker = rq.get_worker()
worker.work()
ic()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)
