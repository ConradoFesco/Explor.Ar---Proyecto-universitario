# src/web/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
print(Session)
db = SQLAlchemy()
migrate = Migrate()
session_ext = Session() 
