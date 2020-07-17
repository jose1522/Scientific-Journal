from flask import Blueprint, session, render_template, request, abort, redirect, url_for, flash, make_response
from database import forms, models, schemas
from core import *
import core
from core.util import dictTools
import os
from sqlalchemy.exc import IntegrityError
import json
import yaml
import uuid
from werkzeug.utils import  secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from datetime import datetime
from functools import wraps
from flask_login import login_required, logout_user, current_user, login_user
from . import login_manager


from database.models import *

admin = Blueprint('admin', '__name__')
conf = yaml.full_load(open("database/formConfig.yml"))
links = list(map(lambda x: (conf.get(x).get('description'),x),conf))


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        payload = Person.query.get(user_id)
        return payload
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('admin.login'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS')


def encryptData(unencryptedData):
    key = app.config.get('ENCRYPTION_KEY')
    cipher_suite = Fernet(bytes(key.encode()))
    encryptedData = cipher_suite.encrypt(bytes(unencryptedData.encode()))
    return encryptedData


def logActivity(modelInstance:Model, activityDescription:dict, isError:bool=False):
    if hasattr(modelInstance, "__tablename__"):
        table_name = modelInstance.__tablename__
    else:
        table_name = modelInstance

    if isError:
        newRecord = ErrorLog(
                            id = 0,
                            person_id = session['id'],
                            date_time = datetime.today(),
                            table_name_id = table_name,
                            description = activityDescription['description'],
                            summary = activityDescription['summary']
        )
        db.session.add(newRecord)
        db.session.commit()
    else :
        newRecord = ActivityLog(
                            id = 0,
                            table_name_id = table_name,
                            person_id = session['id'],
                            date_time = datetime.today(),
                            description = activityDescription['description']
        )
        db.session.add(newRecord)


@admin.route('/')
@login_required
def index():
    # print(session)
    user = Person.query.get(session.get('_user_id'))
    return render_template('private/private_page.html', firstName=user.name, links=links)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(nickname=form.nickname.data).first()
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
    model = Person
    tableName = model.__tablename__
    formName = 'personForm'
    htmlName = 'person_form.html'
    imageFields = ['signature', 'photo']
    foreignKeyMappings ={'degree_id': 'degree', 'job_id': 'job'}
    newForm = True
    idParameter = request.args.get('id') if request.args else None
    formTemplate:forms.ModelForm = getattr(forms, formName)
    formInstance = formTemplate() # instantiate the class
    req = request.form

    def redirectToDefaultRoute():
        return redirect(url_for('admin.index'))

    def populateDataModel(modelInstance):
        # Updates the form instance with values from the website
        for item in formInstance.data:
            try:
                if item != 'csrf_token':
                    if hasattr(modelInstance,item) and item != 'password':
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

    if request.method == 'GET':
        if idParameter:
            newForm = False
            try:
                # Gets the data from the DB
                modelInstance = model.query.get(idParameter)

                # Raises an exception if the ID doesn't exist
                if modelInstance is None:
                    raise Exception('ID {0} not found'.format(idParameter))

                # Checks if the record hasn't been soft-deleted
                if hasattr(modelInstance, 'active'):
                    abort(400) if modelInstance.__getattribute__('active') == 0 else None
                formInstance = formTemplate(obj=modelInstance)

                # Select current value in dropdown menu
                for field in formInstance:
                    if field.name in foreignKeyMappings:
                        formInstance[field.name].data = getattr(modelInstance, foreignKeyMappings[field.name])

                # Log request to the DB
                logActivity(modelInstance, {'summary': '', 'description': '{0} request for ID {1}'.format(request.method, idParameter)})
                db.session.commit()

            except Exception as e:
                modelInstance = model()
                # Log error to the DB
                logActivity(modelInstance, {'summary': str(e), 'description': '{0} request'.format(request.method)},True)
                db.session.commit()
                abort(404)
    else:
        # req = request.form
        buttonClicked = str(req['form_button']).lower()
        modelInstance = model()

        if buttonClicked == 'create':

            try:
                # Encrypt the password and update the form instance
                password = req['password']
                if password is None or password == '':
                    raise Exception("Error! Password field cannot be empty")
                else:
                    # password = encryptData(password).decode(encoding='UTF-8')
                    password = generate_password_hash(password, method='sha256')

                # Creates lists for column names and values to be inserted in DML syntax
                formFieldNames = [x for x in list(formInstance.data.keys()) if x not in ['csrf_token', 'password', 'isAdmin'] and x in req]
                formFieldValues = [x for x in list(map(lambda x: "'{0}'".format(req[x]) if x in req and x not in ['password','isAdmin'] else None, formFieldNames)) if x is not None]

                # Convert boolean value to integer
                isAdmin = 1 if formInstance.isAdmin.data else 0

                # Append the encrypted password and isAdmin to the lists
                formFieldNames.append('password')
                formFieldNames.append('isAdmin')
                formFieldValues.append("'{0}'".format(password))
                formFieldValues.append("'{0}'".format(isAdmin))

                if formInstance.validate_on_submit():
                    for field in imageFields:
                        f = getattr(formInstance, field)
                        filename = secure_filename(f.data.filename)
                        if filename != '':
                            # Sets a unique name for the file and replaces the name in the form
                            uniqueID = str(uuid.uuid4()) + "." + f.data.filename.rsplit('.', 1)[1].lower()
                            f.data.filename = uniqueID
                            formInstance.__setattr__(field, f)

                            # Saves the image in the server
                            f.data.save(os.path.join(
                                app.config.get('UPLOAD_FOLDER'), uniqueID
                            ))

                            # Adds the file to the list before insert
                            formFieldNames.append(field)
                            formFieldValues.append("'"+uniqueID+"'")

                    # Makes insert and commits
                    db.session.execute("Insert into {0} ({1}) values ({2})".format(tableName, ", ".join(formFieldNames),", ".join(formFieldValues)))
                    logActivity(modelInstance, {'summary': '', 'description': '{0} request ({1})'.format(request.method, buttonClicked)})
                    db.session.commit()
                    return redirectToDefaultRoute()

            except Exception as e:
                if len(formInstance.errors.items()) > 0:
                    flashErrors()
                    logActivity(modelInstance, {'summary': ';'.join(formInstance.errors.items()), 'description': '{0} request ({1})'.format(request.method, buttonClicked)},True)
                else:
                    flashErrors(str(e))
                    logActivity(modelInstance, {'summary': ';'.join(formInstance.errors.items()), 'description': '{0} request ({1})'.format(request.method, buttonClicked)}, True)
                db.session.commit()

        elif idParameter:
            try:
                if buttonClicked == 'delete':
                    modelInstance = model.query.get(request.args.get('id'))
                    if hasattr(modelInstance, 'active'):
                        modelInstance.__setattr__('active', '0')
                        db.session.add(modelInstance)
                    else:
                        db.session.delete(modelInstance)

                elif formInstance.validate_on_submit():
                    modelInstance = populateDataModel(model.query.get(request.args.get('id')))

                    # Convert boolean value to integer
                    modelInstance.isAdmin = 1 if formInstance.isAdmin.data else 0

                    # Updating password if a new one is specified
                    newPasswordEntered = req['password']
                    if newPasswordEntered is not None and newPasswordEntered != '':
                        modelInstance.password = encryptData(req['password']).decode(encoding='UTF-8')

                    # Save images submitted by form
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
                                app.config.get('UPLOAD_FOLDER'), uniqueID
                            ))

                    db.session.add(modelInstance)
                    newForm = False

                # Create log in the DB
                logActivity(modelInstance, {'summary': '', 'description': '{0} request ({1}) for id {2}'.format(request.method, buttonClicked, idParameter)})
                db.session.commit()

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

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm, links=links))
    return resp


@admin.route("/form/<name>", methods = ['GET','POST'])
@login_required
def formCRUD(name):

    try:
        objectSpecificConfig = conf[name.lower()]
    except:
        abort(404)

    model = getattr(models, objectSpecificConfig['modelName'])
    tableName = model.__tablename__
    formName = objectSpecificConfig['formName']
    htmlName = objectSpecificConfig['htmlName']
    foreignKeyMappings ={}
    temp = list(map(lambda itemFromConfig: foreignKeyMappings.update(itemFromConfig.items()), objectSpecificConfig['foreignKeyMappings']))  if 'foreignKeyMappings' in objectSpecificConfig else None
    newForm = True
    idParameter = request.args.get('id') if request.args else None


    formTemplate:forms.ModelForm = getattr(forms, formName)
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

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm, links=links))
    return resp


@admin.route("experiment", methods = ['GET', 'POST'])
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

    def getExperimentEquipmentArray(id=None):
        if id is not None:
            equipment = Equipment.query.join(t_experiment_equipment).join(Experiment).filter( (t_experiment_equipment.c.experiment_id == id) & (t_experiment_equipment.c.active == True)).all()
        else:
            equipment =  Equipment.query.join(t_experiment_equipment).join(Experiment).filter(t_experiment_equipment.c.active == True).all()

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
                                core.app.config.get('UPLOAD_FOLDER'), uniqueID
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
                                item.save(os.path.join(core.app.config.get('UPLOAD_FOLDER'), uniqueID))
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

    resp = make_response(render_template("private/experiment_form.html", form=experimentForm, newForm=newForm, equipmentList=equipment, methodologyList=methodology, equipmentSelection=equipmentSelection, links=links))
    return resp

@admin.route("table/<name>")
@login_required
def query_results(name):
    model = Person.query.all()
    modelSchema = schemas.PersonSchema(many=True)
    items = modelSchema.dump(model)
    return render_template('private/query_results.html', query_results=model, items=items)

@admin.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


