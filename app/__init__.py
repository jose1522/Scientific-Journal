from flask import Flask
import datetime
from flask_session import Session

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.permanent_session_lifetime = datetime.timedelta(days=1)
sess = Session()
sess.init_app(app)
from app import views
