from os import environ
import redis
from dotenv import load_dotenv
load_dotenv()

# Image Uploads
UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * (1024 ** 2) # Max image size is 16Mb

class BaseConfig:
    SECRET_KEY = environ.get('SECRET_KEY')
    ENCRYPTION_KEY = environ.get('ENCRYPTION_KEY')
    API_KEY = environ.get('API_KEY')
    SENDGRID_KEY = environ.get('SENDGRID_KEY')
    WTF_CSRF_SECRET_KEY = environ.get('WTF_CSRF_SECRET_KEY')
    RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')
    SESSION_TYPE = environ.get('SESSION_TYPE')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class freeTDSConf(BaseConfig):
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALQUEMY_DATABASE_URL_FREETDS')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS_LOCAL'))

class freeTDSConfLocal(BaseConfig):
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALQUEMY_DATABASE_URL_FREETDS_LOCAL')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS_LOCAL'))

class msodbcConf(BaseConfig):
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALQUEMY_DATABASE_URL_MSODBC')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))

class msodbcConfLocal(BaseConfig):
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALQUEMY_DATABASE_URL_MSODBC_LOCAL')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS_LOCAL'))


