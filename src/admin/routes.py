from flask import Blueprint, session, render_template, request, abort, redirect, url_for, flash, make_response
from flask_login import login_required, logout_user, current_user, login_user
from database import forms, models, schemas
from database.models import *
from core import *
from werkzeug.utils import  secure_filename
from cryptography.fernet import Fernet
from datetime import datetime
from functools import wraps
from . import login_manager
from core import settings
import os
import json
import yaml
import uuid

admin = Blueprint('admin', '__name__')
wd = os.getcwd()
print(os.path.exists(os.path.join(wd,'src')))
if not os.path.exists(os.path.join(wd, 'database')):
    wd = os.path.join(wd, 'src')
formConf = yaml.full_load(open(os.path.join(wd, "database/formConfig.yml")))
viewConf = yaml.full_load(open(os.path.join(wd, "database/viewConfig.yml")))
links = list(map(lambda x: (formConf.get(x).get('description'), x, formConf.get(x).get('accessLevel')), formConf))
views = list(map(lambda x: (viewConf.get(x).get('description'), x, viewConf.get(x).get('accessLevel')), viewConf))


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        payload = Person.getByID(user_id)
        return payload
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('admin.login'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS


def encryptData(unencryptedData):
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(bytes(key.encode()))
    encryptedData = cipher_suite.encrypt(bytes(unencryptedData.encode()))
    return encryptedData


def logActivity(modelInstance:Model, activityDescription:dict, isError:bool=False):
    if hasattr(modelInstance, "__tablename__"):
        table_name = modelInstance.__tablename__
    else:
        table_name = modelInstance

    if isError:
        newID = TableRef.getNextID('error_log')
        newRecord = ErrorLog(
                            id=newID,
                            person_id=current_user.id,
                            date_time=datetime.today(),
                            table_name_id=table_name,
                            description=activityDescription['description'],
                            summary=activityDescription['summary']
        )
        newRecord.save()
    else:
        newID = TableRef.getNextID('activity_log')
        newRecord = ActivityLog(
                            id=newID,
                            table_name_id=table_name,
                            person_id=current_user.id,
                            date_time=datetime.today(),
                            description=activityDescription['description']
        )
        newRecord.save()


def getUserClearance():
    try:
        c = current_user
        return 1 if c.isAdmin else 0
    except:
        return 1


def hasClearance(f):
    # method wraps other functions
    @wraps(f)
    def wrap(*args, **kwargs):
        clearance = getUserClearance(session.get('_user_id'))
        if clearance == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap


@admin.route('/')
@login_required
def index():
    # print(session)
    clearance = getUserClearance()
    res = make_response(render_template('private/private_page.html', firstName=current_user.name, links=links, views=views, userClearance=clearance))
    return res


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = Person.getByNickname(form.nickname.data)
        if user and user.check_password(password=form.password.data):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username/password combination', 'danger')
            return redirect(url_for('admin.login'))
    return render_template('private/login.html', form=form)


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route("/user", methods=['GET','POST'])
@login_required
def userCRUD():
    userClearance = getUserClearance()
    model = Person
    tableName = model.__tablename__
    formName = 'personForm'
    htmlName = 'person_form.html'
    imageFields = ['signature', 'photo']
    foreignKeyMappings = {'degree_id': 'degree', 'job_id': 'job'}
    newForm = True
    idParameter = request.args.get('id') if request.args else None
    formTemplate: forms.ModelForm = getattr(forms, formName)
    formInstance = formTemplate() # instantiate the class
    req = request.form

    def redirectToDefaultRoute():
        return redirect(url_for('admin.index'))

    def populateDataModel(modelInstance):
        # Updates the form instance with values from the website
        for item in formInstance.data:
            try:
                if item != 'csrf_token':
                    if hasattr(modelInstance, item):
                        modelInstance.__setattr__(item, req[item])
            except:
                continue
        return modelInstance

    def flashErrors(errMessage=None):
        # Displays errors into the website
        db.session.rollback()
        if not errMessage:
            for fieldName, errorMessages in formInstance.errors.items():
                for err in errorMessages:
                    flash("Error! Field name: {0}; Error: {1}".format(fieldName, err), category='danger')
        else:
            flash(errMessage, category='danger')

    def saveImages():
        for field in imageFields:
            f = getattr(formInstance, field).data
            filename = secure_filename(f.filename)
            if filename != '':
                # Sets a unique name for the file and replaces the name in the form
                uniqueID = str(uuid.uuid4()) + "." + f.filename.rsplit('.', 1)[1].lower()
                f.filename = uniqueID
                modelInstance.__setattr__(field, f.filename)

                # Saves the image in the server
                f.save(os.path.join(
                    settings.UPLOAD_FOLDER, uniqueID
                ))

    if request.method == 'GET':
        if idParameter:
            newForm = False
            try:
                # Gets the data from the DB
                modelInstance = model.getByID(idParameter)

                # Raises an exception if the ID doesn't exist
                if not modelInstance:
                    raise Exception('ID {0} not found'.format(idParameter))

                # Updates relations
                formInstance = formTemplate(obj=modelInstance)
                fkData = modelInstance.fkToDict()
                for key, value in fkData.items():
                    if key in formInstance:
                        formInstance[key].data = value

            except Exception as e:
                modelInstance = model()
                # Log error to the DB
                logActivity(modelInstance, {'summary': str(e), 'description': '{0} request'.format(request.method)},True)
                abort(404)
    else:
        # req = request.form
        buttonClicked = str(req['form_button']).lower()
        modelInstance = model()

        if buttonClicked == 'create':

            try:
                # Encrypt the password and update the form instance
                if req['password'] is None or req['password'] == '':
                    raise Exception("Error! Password field cannot be empty")

                if formInstance.validate_on_submit():
                    newID = TableRef.getNextID(tableName)
                    populateDataModel(modelInstance)
                    modelInstance.id = newID
                    saveImages()
                    modelInstance.save()
                    return redirectToDefaultRoute()

            except Exception as e:
                if len(formInstance.errors.items()) > 0:
                    flashErrors()
                    logActivity(modelInstance, {'summary': ';'.join(formInstance.errors.items()), 'description': '{0} request ({1})'.format(request.method, buttonClicked)},True)
                else:
                    flashErrors(str(e))
                    logActivity(modelInstance, {'summary': ';'.join(formInstance.errors.items()), 'description': '{0} request ({1})'.format(request.method, buttonClicked)}, True)

        elif idParameter:
            try:
                if buttonClicked == 'delete':
                    modelInstance = model.getByID(request.args.get('id'))
                    modelInstance.delete()

                elif formInstance.validate_on_submit():
                    modelInstance = populateDataModel(model.getByID(request.args.get('id')))
                    saveImages()
                    modelInstance.save()
                    newForm = False

                # Create log in the DB
                logActivity(modelInstance, {'summary': '', 'description': '{0} request ({1}) for id {2}'.format(request.method, buttonClicked, idParameter)})

                if buttonClicked == 'delete':
                    return redirectToDefaultRoute()
                else:
                    flash('Form submitted successfully!', category='success')

            except Exception as e:
                flashErrors(str(e))
                logActivity(modelInstance, {'summary': ';'.join(formInstance.errors.items()), 'description': '{0} request ({1}) for id {2}'.format(request.method, buttonClicked, idParameter)}, True)
                db.session.commit()
        else:
            flash('No id was provided', category='danger')
            logActivity(modelInstance, {'summary': 'No id was provided', 'description': '{0} request ({1})'.format(request.method, buttonClicked)}, True)
            db.session.commit()

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm, links=links, views=views, userClearance=userClearance))
    return resp


@admin.route("/form/<name>", methods = ['GET','POST'])
@login_required
def formCRUD(name):

    try:
        objectSpecificConfig = formConf[name.lower()]
    except:
        abort(404)

    userClearance = getUserClearance()

    if objectSpecificConfig['accessLevel'] > userClearance:
        abort(404)

    model = getattr(models, objectSpecificConfig['modelName'])
    tableName = model.__tablename__
    formName = objectSpecificConfig['formName']
    htmlName = objectSpecificConfig['htmlName']
    foreignKeyMappings ={}
    temp = list(map(lambda itemFromConfig: foreignKeyMappings.update(itemFromConfig.items()), objectSpecificConfig['foreignKeyMappings']))  if 'foreignKeyMappings' in objectSpecificConfig else None
    newForm = True
    idParameter = request.args.get('id') if request.args else None


    formTemplate: forms.ModelForm = getattr(forms, formName)
    formInstance = formTemplate() # instantiate the class

    def redirectToDefaultRoute():
        return redirect(url_for('admin.index'))

    def populateDataModel(modelInstance):
        for item in formInstance.data:
            try:
                if item != 'csrf_token':
                    if hasattr(modelInstance,item):
                        modelInstance.__setattr__(item, req[item])
            except:
                continue
        return modelInstance

    def flashErrors(errMessage=None):
        db.session.rollback()
        if not errMessage:
               for fieldName, errorMessages in formInstance.errors.items():
                for err in errorMessages:
                    flash("Error! Field name: {0}; Error: {1}".format(fieldName, err), category='danger')
        else:
                flash(errMessage, category='danger')

    if request.method == 'GET':
        modelInstance = model()
        if idParameter:
            newForm = False
            try:
                modelInstance = model.query.get(idParameter)
                if modelInstance is None:
                    raise Exception('ID {0} not found'.format(idParameter))

                if hasattr(modelInstance, 'active'):
                    abort(400) if modelInstance.__getattribute__('active') == 0 else None
                formInstance = formTemplate(obj=modelInstance)

                # Select current value in dropdown menu
                for field in formInstance:
                    """
                    When a form has a foreign key (FK), select fields are used 
                    to make the information more readable to the user; here we use
                    a tuple to send the FK with a meaningful value.
                    
                    These FKs have names that follow the pattern "foreignKeyName_id",
                    but only store the value of the Primary Key (PK). 
                    
                    The models also have objects for each relationship in the table,
                    which have all the fields from the other table. These objects are
                    used to populate the select fields, and their names follow the 
                    pattern "foreignKeyName
                    """
                    if field.name in foreignKeyMappings:
                        formInstance[field.name].data = getattr(modelInstance, foreignKeyMappings[field.name])
                logActivity(modelInstance,{'summary':'GET HTTP Call','description' :'GET Request with argument id: '+ idParameter},False)
            except Exception as e:
                modelInstance = model()
                logActivity(modelInstance, {'summary': str(e), 'description': '{0} request'.format(request.method)}, True)
                abort(404)
        # else:
        #     logActivity(modelInstance, {'summary': '', 'description': '{0} request'.format(request.method)})
    else:
        req = request.form
        buttonClicked = str(req['form_button']).lower()
        modelInstance = model()

        if buttonClicked == 'create':
            formFieldNames = [x for x in list(formInstance.data.keys()) if x != 'csrf_token']
            formFieldValues = list(map(lambda x: "'{}'".format(req[x]), formFieldNames))

            if formInstance.validate_on_submit():
                try:
                    db.session.execute("Insert into {0} ({1}) values ({2})".format(tableName, ", ".join(formFieldNames),", ".join(formFieldValues)))
                    logActivity(modelInstance, {'summary': 'New record added', 'description': 'POST Request (Create)'})
                    db.session.commit()
                    flash('Form submitted successfully!', category='success')
                    return redirectToDefaultRoute()

                except Exception as e:
                    logActivity(modelInstance, {'summary': str(e), 'description': 'POST Request (Create)'}, True)
                    flashErrors(str(e))
            else:
                logActivity(modelInstance, {'summary': ";".join(formInstance.errors.items()), 'description': 'POST Request ({0})'.format(buttonClicked)}, True)
                flashErrors()

        elif idParameter:
            try:
                if buttonClicked == 'delete':
                    modelInstance = model.query.get(request.args.get('id'))
                    if hasattr(model, 'active'):
                        model.__setattr__('active', '0')
                        db.session.add(modelInstance)
                        newForm = True
                    else:
                        db.session.delete(modelInstance)

                elif formInstance.validate_on_submit():
                    modelInstance = populateDataModel(model.query.get(request.args.get('id')))
                    db.session.add(modelInstance)
                    newForm = False

                logActivity(modelInstance, {'summary': "", 'description': 'POST Request ({0}) for ID {1}'.format(buttonClicked,idParameter)})
                db.session.commit()  # commit after logActivity
                if newForm:
                    return redirectToDefaultRoute()  # Redirect to default route
                else:
                    flash('Form submitted successfully!', category='success')

            except Exception as e:
                flashErrors(str(e)) # this already includes rollback
                logActivity(modelInstance, {'summary': str(e), 'description': 'POST Request ({0}) for ID {1}'.format(buttonClicked,idParameter)}, True)
                db.session.commit()

        else:
            logActivity(modelInstance, {'summary': "User did not provide an ID parameter", 'description': 'POST Request'}, True)
            flash('No id was provided',category='danger')

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm, links=links, views=views, userClearance=userClearance))
    return resp


@admin.route("experiment", methods=['GET', 'POST'])
@login_required
def experimentCRUD():

    def getEquipmentArray(id=None):
        if id is not None:
            equipment = Equipment.query.get(id)
        else:
            equipment = Equipment.query.all()

        try:
            if isinstance(equipment, list):
                return list(map(lambda x: {'value': x.id, 'name': "{0}, {1}".format(x.name, x.serial)}, equipment))
            else:
                return [{'value': equipment.id, 'name': "{0}, {1}".format(equipment.name, equipment.serial)}]
        except:
            return []

    def getExperimentEquipmentArray(id:str=None):
        if id is not None:
            equipment = Equipment.getByID(id)
        else:
            equipment = ExperimentEquipment.getByAll()

        try:
            if isinstance(equipment, list):
                return list(map(lambda x: {'value': x.id, 'name': "{0}, {1}".format(x.name, x.serial)}, equipment))
            else:
                return [{'value': equipment.id, 'name': "{0}, {1}".format(equipment.name, equipment.serial)}]
        except:
            return []

    def getMethodologyArray(id=None):
        if id is not None:
            methodology = Methodology.query.join(Experiment).filter( (Methodology.experiment_id == id) & (Methodology.active == True)).all()
        else:
            methodology = Methodology.query.join(Experiment).filter(Methodology.active == True).all()
        try:
            if isinstance(methodology, list):
                l = list(map(lambda x: {'value': x.id, 'name': "{0}".format(x.description)}, methodology))
                l.sort(key=lambda x: x['value'])
                return l
            else:
                return [{'value': methodology.id, 'name': "{0}".format( methodology.description)}]
        except Exception as e:
            print(str(e))
            return []

    def getExperimentData(id):
        experiment = Experiment.query.get(id)

        if experiment is None:
            abort(404)
        if hasattr(experiment, 'active'):
            abort(404) if experiment.active == 0 else None
        return experiment

    def insertIntoTable(tableName,columns,values):
        try:
            db.session.execute("Insert into {0} ({1}) values ({2})".format(tableName, columns, values))
        except Exception as e:
            raise Exception(str(e))

    def redirectToDefaultRoute():
        experimentForm = forms.experimentForm()
        newForm = True
        equipment = getEquipmentArray()
        methodology = None
        equipmentSelection = None
        return redirect(url_for('admin.index'))

    def flashErrors(errMessage=None, formInstance=None):
        db.session.rollback()
        if not errMessage:
               for fieldName, errorMessages in formInstance.errors.items():
                for err in errorMessages:
                    flash("Error! Field name: {0}; Error: {1}".format(fieldName, err), category='danger')
        else:
                flash(errMessage, category='danger')

    userClearance = getUserClearance()
    experimentForm = forms.experimentForm()
    newForm = True
    equipment = getEquipmentArray()
    equipmentSelection = None
    methodology = None

    if request.method == 'GET':
        if request.args.get('id'): # If no ID, then the standard blank template will be rendered
            idValue = request.args.get('id')
            experimentData = getExperimentData(idValue)  # this has error handler for id not found. Must go first
            equipmentSelection = getExperimentEquipmentArray(idValue)
            methodology = getMethodologyArray(idValue)
            experimentForm = forms.experimentForm(obj=experimentData)

            # Data for queryselect objects needs to be an object, but they come as int by default
            experimentForm.project_id.data = experimentData.project
            experimentForm.experimenter_id.data = experimentData.experimenter
            experimentForm.witness_id.data = experimentData.witness
            newForm = False

    else:
        f = request.form
        action = f['form_button']
        if action == 'create':
            try:
                if experimentForm.validate_on_submit():
                    # Prepare list for manual insert
                    fieldList = ['name', 'date', 'description', 'main_objective', 'project_id', 'experimenter_id', 'witness_id']
                    valueList = list(map(lambda x: "'{0}'".format(f[x]),fieldList))

                    # Insert data and retrieve new record
                    insertIntoTable("experiment", ", ".join(fieldList), ", ".join(valueList))
                    newExperiment = Experiment.query.filter((Experiment.project_id == f['project_id']) & (Experiment.name == f['name'])).first()

                    # Insert Methodology
                    methodologyList = []
                    for key, value in f.items():
                        if 'methodology' in key: methodologyList.append(value)

                     # if len(methodologyList) > 1:
                    stepIndex = 0
                    for item in methodologyList:
                        columns = ['step', 'description', 'experiment_id']
                        values = [str(stepIndex), "'{0}'".format(item), str(newExperiment.id)]
                        insertIntoTable('methodology', ' , '.join(columns), ' , '.join(values))
                        stepIndex += 1

                    # Insert Equipment
                    if f['equipment'] is not None:
                        equipmentList:list = f['equipment'].split(',')
                        for item in equipmentList:
                            if item != '':
                                columns = ['experiment_id','equipment_id']
                                values = [str(newExperiment.id),str(item)]
                                insertIntoTable('experiment_equipment', ' , '.join(columns), ' , '.join(values))

                    # Save the images to the server and store the names in the DB
                    for item in experimentForm.photos.data:
                        filename = secure_filename(item.filename)
                        if filename != '':
                            # Sets a unique name for the file and replaces the name in the form
                            uniqueID = str(uuid.uuid4()) + "." + item.filename.rsplit('.', 1)[1].lower()
                            item.filename = uniqueID
                            # Saves the image in the server
                            item.save(os.path.join(
                                settings.UPLOAD_FOLDER, uniqueID
                            ))
                            insertIntoTable('experiment_image', 'photo,experiment_id',"'{0}','{1}'".format(uniqueID, newExperiment.id))

                    logActivity(Experiment, {'summary': '', 'description': '{0} request: create new record'.format(request.method)})
                    db.session.commit()
                    flash('New experiment created', 'success')
                    redirectToDefaultRoute()
                else:
                    db.session.rollback()
                    logActivity(Experiment, {'summary': 'Experiment create error', 'description': '{0} request: create new record'.format(request.method)}, isError=True)
                    db.session.commit()
                    flashErrors(formInstance=experimentForm)
            except Exception as e:
                db.session.rollback()
                logActivity(Experiment,{'summary': 'Experiment create error', 'description': '{0} request: create new record'.format(request.method)}, isError=True)
                db.session.commit()
                flash(str(e), 'danger')


        elif request.args.get('id'): # If no ID, then the standard blank template will be rendered
            idValue = request.args.get('id')
            originalRecord = getExperimentData(idValue)
            if (action == 'update'):
                try:
                    if experimentForm.validate_on_submit():

                        # Modify columns from original experiment record
                        experimentForm.populate_obj(originalRecord)
                        originalRecord.project_id = f['project_id']
                        originalRecord.experimenter_id = f['experimenter_id']
                        originalRecord.witness_id = f['witness_id']
                        db.session.add(originalRecord)
                        logActivity(Experiment, {'summary': '', 'description': '{0} request for ID {1}'.format(request.method, idValue)})

                        # Update Methodology
                        originalMethodologyList = getMethodologyArray(idValue)
                        originalMethodologyList = dict(map(lambda x: x.values(), originalMethodologyList))
                        newMethodologyList = {}
                        for item in f.items():
                            key, value = item
                            if 'methodology' in key:
                                key = key.split('_').pop()
                                newMethodologyList.update({key:value})

                        if len(newMethodologyList)>0:
                            for item in newMethodologyList.items():
                                key, value = item
                                insertIntoTable('methodology', 'experiment_id, step, description', "'{0}','{1}','{2}'".format(idValue, key, value))
                                logActivity(Methodology, {'summary': '', 'description': '{0} request for ID {1} (Create)'.format(request.method, idValue)})

                        if len(originalMethodologyList) > 0:
                            for item in originalMethodologyList.items():
                                key, value = item
                                # originalRecord = Methodology.query.filter((Methodology.experiment_id == idValue) & (Methodology.id == key)).first()
                                # originalRecord.active = 0
                                # db.session.add(originalRecord)
                                Methodology.query.filter((Methodology.experiment_id == idValue) & (Methodology.id == key)).delete()
                                logActivity(Methodology, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, key)})

                        # Update Equipment
                        if 'originalEquipmentList' in f:
                            originalEquipmentList = f['originalEquipmentList'].replace("\'",'"')
                            originalEquipmentList = json.loads(originalEquipmentList)
                            originalEquipmentList = set(map(lambda x: str(x['value']),originalEquipmentList))
                        else:
                            originalEquipmentList = None
                        newEquipmentList = f['equipment']
                        if len(newEquipmentList) > 0: newEquipmentList = set(newEquipmentList.split(','))
                        addedEquipmentRecords = (newEquipmentList - originalEquipmentList) if originalEquipmentList is not None else newEquipmentList
                        removedEquipmentRecords = originalEquipmentList - newEquipmentList if originalEquipmentList is not None else []

                        if len(addedEquipmentRecords) > 0:
                            for item in addedEquipmentRecords:
                                insertIntoTable('experiment_equipment', 'experiment_id, equipment_id', "'{0}','{1}'".format(idValue, item))
                                logActivity('experiment_equipment', {'summary': '', 'description': '{0} request for Experiment iid {1} (Create)'.format(request.method, idValue)})

                        if len(removedEquipmentRecords) > 0:
                            for item in removedEquipmentRecords:
                                db.session.execute('update experiment_equipment set active = 0 where experiment_id = {0} and equipment_id = {1}'.format(idValue,item))
                                logActivity('experiment_equipment', {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, item)})

                        # Save the images to the server and store the names in the DB
                        for item in experimentForm.photos.data:
                            filename = secure_filename(item.filename)
                            originalExperimentImages = ExperimentImage.query.filter(ExperimentImage.experiment_id == idValue).all()

                            if filename != '':
                                # Sets a unique name for the file and replaces the name in the form
                                uniqueID = str(uuid.uuid4()) + "." + item.filename.rsplit('.', 1)[1].lower()
                                item.filename = uniqueID
                                # Saves the image in the server
                                item.save(os.path.join(settings.UPLOAD_FOLDER, uniqueID))
                                insertIntoTable('experiment_image', 'photo,experiment_id', "'{0}','{1}'".format(uniqueID, idValue))
                                logActivity(ExperimentImage, {'summary': '', 'description': '{0} request for Experiment id {1} (Create)'.format(request.method, idValue)})

                            if originalExperimentImages is not None:
                                for item in originalExperimentImages:
                                    item.active = 0
                                    db.session.add(item)
                                    logActivity(ExperimentImage, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, item)})

                        db.session.commit()
                        return redirect(url_for('admin.experimentCRUD', id=idValue, links=links))

                    else:
                        db.session.rollback()
                        logActivity(Experiment, {'summary': 'Experiment update error', 'description': '{0} request for ID {1} (Update)'.format(request.method, idValue)}, isError=True)
                        db.session.commit()
                        flashErrors(experimentForm)
                        newForm = False

                except Exception as e:
                    db.session.rollback()
                    logActivity(Methodology, {'summary': 'Experiment update error', 'description': '{0} request for ID {1} (Remove)'.format(request.method, idValue)}, isError=True)
                    db.session.commit()
                    flashErrors(str(e))
                    newForm = False

            elif action == 'delete':
                try:
                    # Delete experiment
                    experimentRecord = Experiment.query.get(idValue)
                    experimentRecord.active = 0
                    db.session.add(experimentRecord)
                    logActivity(Experiment, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, idValue)})

                    # Delete methodology
                    methodologyRecords = Methodology.query.filter(Methodology.experiment_id == idValue).all()
                    if methodologyRecords is not None:
                        for record in methodologyRecords:
                            record.active = 0
                            db.session.add(record)
                            logActivity(Methodology, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, record.id)})

                    # Delete methodology
                    methodologyRecords = Methodology.query.filter(Methodology.experiment_id == idValue).all()
                    if methodologyRecords is not None:
                        for record in methodologyRecords:
                            record.active = 0
                            db.session.add(record)
                            logActivity(Methodology, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, record.id)})

                    # Delete equipment
                        db.session.execute('update experiment_equipment set active = 0 where experiment_id = {0}'.format(idValue))
                        logActivity('experiment_equipment', {'summary': '', 'description': '{0} request for Experiment id {1} (Remove All)'.format(request.method, idValue)})

                    # Delete images
                    equipmentRecords = ExperimentImage.query.filter(ExperimentImage.experiment_id == idValue).all()
                    for record in equipmentRecords:
                        record.active = 0
                        db.session.add(record)
                        logActivity(Methodology, {'summary': '', 'description': '{0} request for ID {1} (Remove)'.format(request.method, record.id)})

                    redirectToDefaultRoute()

                except Exception as e:
                    db.session.rollback()
                    logActivity(Methodology, {'summary': 'Experiment delete error', 'description': '{0} request for ID {1} (Remove)'.format(request.method, idValue)}, isError=True)
                    db.session.commit()
                    flashErrors(str(e))
                    newForm = False

    resp = make_response(render_template("private/experiment_form.html", form=experimentForm, newForm=newForm, equipmentList=equipment, methodologyList=methodology, equipmentSelection=equipmentSelection, links=links, views=views, userClearance=userClearance))
    return resp


@admin.route("table/<name>")
@login_required
def query_results(name):
    try:
        objectSpecificConfig = viewConf[name.lower()]
        userClearance = getUserClearance()
        if objectSpecificConfig['accessLevel'] > userClearance:
            abort(404)
        view = getattr(models, objectSpecificConfig['viewName'])
        model = db.session.query(view).all()
        modelSchema = getattr(schemas, objectSpecificConfig['schema'])
        modelSchema = modelSchema(many=True)
        items = modelSchema.dump(model)

        return render_template('private/query_results.html', query_results=model, items=items, links=links, views=views, userClearance=userClearance)
    except Exception as e:
        print(str(e))
        abort(404)

@admin.route("/test")
@login_required
def test():
    return render_template('private/api_call.html', links=links, views=views, userClearance=getUserClearance())

@admin.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


