from flask import Blueprint, session, render_template, request
from wtforms.ext.sqlalchemy.orm import model_form
from database import forms
import json
from database.database import db

from database.models import *
admin = Blueprint('admin', '__name__')

@admin.route('/')
def index():
    return "Hello World"

@admin.route("/user")
def displayUser():
    return session['user']

@admin.route("/consecutive-form", methods = ['GET','POST'])
def consecutiveForm():

    modelObject = Consecutive
    formName = 'consecutiveForm'
    fieldsToUpdate = {'table_name_id': 'table_name', 'type_id': 'type'}
    htmlName = 'sample_form'

    formPlaceholder:forms.ModelForm = getattr(forms, formName)
    form = formPlaceholder() # instantiate the class

    if request.method == 'GET':
        if request.args:
            id = request.args.get('id')
            existingData = modelObject.query.get(id)
            form = formPlaceholder(obj=existingData)

            # Select current vale in dropdown menu
            for field in form:
                if field.name in fieldsToUpdate:
                    form[field.name].data = getattr(existingData, fieldsToUpdate[field.name])

    else:
        if form.validate_on_submit():
            req = request.form
            selectedAction = str(req['form_button']).lower()

            if selectedAction == 'create':
                modelObject = modelObject()
                form.populate_obj(modelObject)
                db.session.add(modelObject)
                # db.session.commit()

            return str(list(map(lambda x: {x: form.data[x]} if x != 'csrf_token' else 'CSRF Token', form.data)))
        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    print("Error! field name: {0}; error: {1}".format(fieldName,err))
    return render_template('private/{0}.html'.format(htmlName), form=form)


@admin.route("/job-form", methods=['GET','POST'])
def jobForm():
    form = forms.jobForm()
    if request.method == 'POST':
        return str(list(map(lambda x: {x: form.data[x]} if x != 'csrf_token' else 'CSRF Token', form.data)))
    return render_template('private/job_form.html', form=form)