from flask import Blueprint, request, abort
from flask_login import current_user, login_required
from googletrans import Translator
from database import models, schemas, db
import yaml
import json

api = Blueprint('api', '__name__')
viewConf = yaml.full_load(open("database/viewConfig.yml"))

def getUserClearance():
    try:
        c = current_user
        return 1 if c.isAdmin else 0
    except:
        return 1

@api.route('/')
@login_required
def index():
    u = current_user
    return "Hello World"

@api.route('/fetch/<name>')
@login_required
def getLogData(name):
    u = current_user
    reqArgs = request.args
    objectSpecificConfig = viewConf[name.lower()]
    userClearance = getUserClearance()

    try:
        reqArgs = request.args
        objectSpecificConfig = viewConf[name.lower()]
        userClearance = getUserClearance()
        viewName = objectSpecificConfig['viewName']
        accessLevel = objectSpecificConfig['accessLevel']
        if  accessLevel > userClearance:
            abort(404)
        view = getattr(models, viewName)
        model = db.session.query(view).all()
        modelSchema = getattr(schemas, objectSpecificConfig['schema'])
        modelSchema = modelSchema(many=True)
        items = modelSchema.dump(model)

        return json.dumps(items)
    except Exception as e:
        print(str(e))
        abort(404)

    return "Hello World"


@api.route('/translate')
def translate():
    sourceText = request.args.get('sourceText')
    targetLanguage = request.args.get('targetLanguage')
    translator = Translator()
    translation = translator.translate(sourceText, dest=targetLanguage)
    translation = {"text":translation.text}
    return json.dumps(translation)

