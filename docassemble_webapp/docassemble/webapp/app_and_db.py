from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def reset_db():
    global db
    if hasattr(db, 'engine'):
        db.engine.dispose()
    db = SQLAlchemy(app)
