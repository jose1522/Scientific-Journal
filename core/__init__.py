import datetime

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_session import Session

from admin.routes import admin
from api.routes import api
from database import db
# from database.database import db
from public.routes import public
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.permanent_session_lifetime = datetime.timedelta(days=1)

# Register blueprints
app.register_blueprint(public)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/admin')

# Instantiate session
sess = Session()
sess.init_app(app)

# Instantiate SQLAlchemy
db.init_app(app)

# Instantiate Flask Bootstrap
Bootstrap(app)

# from core import views

