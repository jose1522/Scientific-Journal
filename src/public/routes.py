from flask import Blueprint, url_for, session, make_response, redirect
from functools import wraps
from database import db, models
from database.models import *
import json
import os
import yaml

public = Blueprint('public', '__name__')

def login_required(f):
    # method wraps other functions
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'userName' in session: #if there is a user key in the session object, continue
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap

@public.route("/")
def index():
    session['user'] = 'Test'
    session['id'] = 0
    res = make_response("Hello World")
    # res.set_cookie("genericCookie", json.dumps({"key1":"value1","key2":"value2"}))
    return res

@public.route("/user")
def displayUser():
    return session['user']

@public.route("/logout")
def logout():
    session.clear()
    return "Goodbye World!"

@public.route("/test")
def test():
    # for item in ['Nanotechonology','Quantum Computing']:
    #     newID = TableRef.getNextID('branch')
    #     newBranch = Branch()
    #     newBranch.name = item
    #     newBranch.id = newID
    #     newBranch.save()
    #
    # branchInfo = Branch.getByID(0)
    # branchInfo.active = '0'
    # branchInfo.save()
    #
    # branchInfo = Branch.getByID(0)
    # print(branchInfo.name)

    equipmentInfo = db.session.query(t_view_branch).all()
    decryptedData = []
    for row in equipmentInfo:
        auxList = []
        for cell in row:
            auxValue = cell
            try:
                if cell.isdigit():
                    auxValue = int(auxValue)
                else:
                    auxValue = models.decryptData(cell)
            except:
                pass
            finally:
                auxList.append(auxValue)
        currentValue = auxList.pop(2)
        auxList[1] = f'{auxList[1]}{auxList[0]+currentValue}'
        decryptedData.append(tuple(auxList))

    return str("Hi")

@public.route("/initdb")
def initDB():
    wd = os.getcwd()
    file = yaml.full_load(open(os.path.join(wd, "src/database/dbInitialization.yml")))
    for className in file:
        for row in file[className]:
            model = getattr(models, className)
            tableName = model.__tablename__
            modelInstance = model()
            if tableName != 'table_ref':
                newID = TableRef.getNextID(tableName)
            for key, value in row.items():
                if key == 'id':
                    value = newID
                if not isinstance(value,str):
                    value = str(value)
                modelInstance.__setattr__(key, value)
            modelInstance.save()
            print(f'{className}: {str(row)}')
    return str("Hi")