from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate()
session_ext = Session()
oauth = OAuth()