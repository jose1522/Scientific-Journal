import datetime
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_session import Session
from admin.routes import admin
from api.routes import api
from database import db, ma
from admin import login_manager
from public.routes import public
from .settings import *

def loadConf(OS, isLocal):
    if OS == 'Darwin':
        if isLocal:
            return freeTDSConfLocal()
        else:
            return freeTDSConf()
    else:
        if isLocal:
            return msodbcConfLocal()
        else:
            return msodbcConf()

def create_app(OS, isLocal=False):

    app = Flask(__name__)
    # app.config.from_pyfile('settings.py')
    app.config.from_object(loadConf(OS, isLocal))
    app.permanent_session_lifetime = datetime.timedelta(days=1)

    # Register blueprints
    app.register_blueprint(public)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin, url_prefix='/admin')

    # Instantiate session
    sess = Session()
    sess.init_app(app)
    login_manager.init_app(app)

    # Instantiate SQLAlchemy
    db.init_app(app)
    ma.init_app(app)

    # Instantiate Flask Bootstrap
    Bootstrap(app)
    return app

