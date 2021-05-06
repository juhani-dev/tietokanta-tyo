from start import start
from flask_sqlalchemy import SQLAlchemy
from os import getenv

start.secret_key = getenv("SECRET_KEY")
start.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(start)