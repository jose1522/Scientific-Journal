from flask import Blueprint, request, abort
from flask_login import current_user, login_required
from googletrans import Translator
from database import models, schemas, db
import yaml
import json
import os

api = Blueprint('api', '__name__')
wd = os.getcwd()
print(os.path.exists(os.path.join(wd,'src')))
if not os.path.exists(os.path.join(wd, 'database')):
    wd = os.path.join(wd, 'src')
viewConf = yaml.full_load(open(os.path.join(wd,"database/viewConfig.yml")))


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

        return items
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


@api.route('/projects/')
def getProjectList():
    response = {}
    reqArgs = request.args
    projects = models.Project.getAllFull(reqArgs)
    projectSchema = schemas.ProjectSchemaFull(many=True)
    projects = projectSchema.dumps(projects)
    projects = projectSchema.loads(projects)
    response.update({'data':projects})
    return response


@api.route('/branches/')
def getBranchList():
    response = {}
    branches = models.Branch.getByAll()
    branchSchema = schemas.BranchSchemaFull(many=True)
    branches = branchSchema.dumps(branches)
    branches = branchSchema.loads(branches)
    response.update({'data':branches})
    return response


@api.route('/authors/')
def getAuthorList():
    response = {}
    authors = models.Person.getByAll()
    personSchema = schemas.PersonSchemaFull(many=True)
    authors = personSchema.dumps(authors)
    authors = personSchema.loads(authors)
    response.update({'data':authors})
    return response


@api.route('/project-info')
def getProjectData():
    reqArgs = request.args
    if 'id' in reqArgs:
        response = {}
        projectID = reqArgs.get('id')
        projects = models.Project.getAllFull(reqArgs)
        projectSchema = schemas.ProjectSchemaFull(many=True)
        projects = projectSchema.loads(projectSchema.dumps(projects))
        response.update({'project':projects})

        experiments, methodology, equipment = models.Experiment.getByAll(projectID)
        experimentSchema = schemas.ExperimentSchemaFull(many=True)
        experiments = experimentSchema.loads(experimentSchema.dumps(experiments))

        auxExperiments = {}
        for i in range(0, len(experiments)):
            item = experiments[i]
            newIndex = int(item.get('id'))
            auxExperiments[newIndex] = experiments[i]

        experiments = auxExperiments

        for i in methodology:
            if isinstance(methodology[i],list):
                methodologySchema = schemas.MethodologySchemaFull(many=True)
            else:
                methodologySchema = schemas.MethodologySchemaFull()
            item = methodologySchema.loads(methodologySchema.dumps(methodology[i]))
            experiments[i]['methodology'] = item



        for i in equipment:
            if isinstance(equipment[i],list):
                equipmentSchema = schemas.EquipmentSchemaFull(many=True)
            else:
                equipmentSchema = schemas.EquipmentSchemaFull()
            item = equipmentSchema.loads(equipmentSchema.dumps(equipment[i]))
            experiments[i]['equipment'] = item

        response.update({'experiments': list(experiments.values())})
        return response
    else:
        return 404, 'id not in arguments'

