from flask import Blueprint, session, render_template, request, abort, redirect, url_for, flash, make_response
from database import forms, models
import core
import os
from sqlalchemy.exc import IntegrityError
import json
import yaml
import uuid
from werkzeug.utils import  secure_filename
from cryptography.fernet import Fernet
from datetime import datetime

from database.models import *
admin = Blueprint('admin', '__name__')
conf = yaml.full_load(open("database/formConfig.yml"))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in core.app.config.get('ALLOWED_EXTENSIONS')

def encryptData(unencryptedData):
    key = core.app.config.get('ENCRYPTION_KEY')
    cipher_suite = Fernet(bytes(key.encode()))
    encryptedData = cipher_suite.encrypt(bytes(unencryptedData.encode()))
    return encryptedData

def logActivity(modelInstance:Model, activityDescription:dict, isError:bool):
    if isError:
        newRecord = ErrorLog(
                            id = 0,
                            person_id = session['id'],
                            date_time = datetime.today(),
                            table_name_id = modelInstance.__tablename__,
                            description = activityDescription['description'],
                            summary = activityDescription['summary']
        )
    else :
        newRecord = ActivityLog(
                            id = 0,
                            table_name_id = modelInstance.__tablename__,
                            person_id = session['id'],
                            date_time = datetime.today(),
                            description = activityDescription['description']
        )
    db.session.add(newRecord)



@admin.route('/')
def index():
    return "Hello World"

@admin.route("/user", methods=['GET','POST'])
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
                    raise Exception('ID not found')

                # Checks if the record hasn't been soft-deleted
                if hasattr(modelInstance, 'active'):
                    abort(400) if modelInstance.__getattribute__('active') == 0 else None
                formInstance = formTemplate(obj=modelInstance)

                # Select current value in dropdown menu
                for field in formInstance:
                    if field.name in foreignKeyMappings:
                        formInstance[field.name].data = getattr(modelInstance, foreignKeyMappings[field.name])
            except:
                abort(404)
    else:
        # req = request.form
        buttonClicked = str(req['form_button']).lower()

        if buttonClicked == 'create':

            try:
                # Encrypt the password and update the form instance
                password = req['password']
                if password is None or password == '':
                    raise Exception("Error! Password field cannot be empty")
                else:
                    password = encryptData(password).decode(encoding='UTF-8')

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
                                core.app.config.get('UPLOAD_FOLDER'), uniqueID
                            ))

                            # Adds the file to the list before insert
                            formFieldNames.append(field)
                            formFieldValues.append("'"+uniqueID+"'")

                    # Makes insert and commits
                    db.session.execute("Insert into {0} ({1}) values ({2})".format(tableName, ", ".join(formFieldNames),", ".join(formFieldValues)))
                    db.session.commit()
                    flash('Form submitted successfully!', category='success')

            except Exception as e:
                flashErrors(str(e))
            else:
                flashErrors()

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
                                core.app.config.get('UPLOAD_FOLDER'), uniqueID
                            ))

                    db.session.add(modelInstance)
                    newForm = False

                db.session.commit()
                flash('Form submitted successfully!', category='success')

            except Exception as e:
                flashErrors()
        else:
            flash('No id was provided', category='danger')

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm))
    return resp


@admin.route("/form/<name>", methods = ['GET','POST'])
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
        if idParameter:
            newForm = False
            try:
                modelInstance = model.query.get(idParameter)
                if modelInstance is None:
                    raise Exception('ID not found')

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
                    
                    The models also have objects for each relationships in the table,
                    which have all the fields from the other table. These objects are
                    used to populate the select fields, and their names follow the 
                    pattern "foreignKeyName
                    """
                    if field.name in foreignKeyMappings:
                        formInstance[field.name].data = getattr(modelInstance, foreignKeyMappings[field.name])
                logActivity(modelInstance,{'summary':'GET HTTP Call','description' :'GET Request with argument id: '+ idParameter},False)
            except Exception as e:
                print(e)
                abort(404)
    else:
        req = request.form
        buttonClicked = str(req['form_button']).lower()

        if buttonClicked == 'create':
            formFieldNames = [x for x in list(formInstance.data.keys()) if x != 'csrf_token']
            formFieldValues = list(map(lambda x: "'{}'".format(req[x]), formFieldNames))

            if formInstance.validate_on_submit():
                try:
                    db.session.execute("Insert into {0} ({1}) values ({2})".format(tableName, ", ".join(formFieldNames),", ".join(formFieldValues)))
                    db.session.commit()
                    flash('Form submitted successfully!', category='success')
                except Exception as e:
                    flashErrors(str(e))
            else:
                flashErrors()

        elif idParameter:
            try:
                if buttonClicked == 'delete':
                    modelInstance = model.query.get(request.args.get('id'))
                    if hasattr(model, 'active'):
                        model.__setattr__('active', '0')
                        db.session.add(modelInstance)
                    else:
                        db.session.delete(modelInstance)

                elif formInstance.validate_on_submit():
                    modelInstance = populateDataModel(model.query.get(request.args.get('id')))
                    db.session.add(modelInstance)
                    newForm = False

                db.session.commit()
                flash('Form submitted successfully!', category='success')

            except Exception as e:
                flashErrors()
        else:
            flash('No id was provided',category='danger')

    resp = make_response(render_template('private/{0}'.format(htmlName), form=formInstance, newForm=newForm))
    return resp


@admin.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404

# @admin.errorhandler(IntegrityError)
# def handle_bad_request(e):
#     db.session.rollback()
#     flash("Error! A duplicate value has been submitted.")
#     return redirect(request.referrer)