# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, Table, Unicode, text, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from core import settings
from cryptography.fernet import Fernet
import copy


Base = db
Model = Base.Model
metadata = Base.metadata


def encryptData(unencryptedData):
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(bytes(key.encode()))
    encryptedData = cipher_suite.encrypt(bytes(unencryptedData.encode()))
    return encryptedData.decode("utf-8")


def decryptData(encryptedData: object) -> object:
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(bytes(key.encode()))
    decryptedData = cipher_suite.decrypt(bytes(encryptedData.encode()))
    return decryptedData.decode("utf-8")


class Branch(Model):
    __tablename__ = 'branch'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False)
    active = Column(Unicode(250), index=True, server_default=text("((1))"))

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.active = decryptData(data.active)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class Code(Model):
    __tablename__ = 'code'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(250), nullable=False, unique=True, info={'label': 'Code Description'})
    available = Column(Integer, server_default=text("((1))"))

    def __repr__(self):
        return str([{"id":self.id}, {"description":self.description}])

    def __init__(self):
        super().__init__()
        self.available = '1'

    def save(self):
        self.description = encryptData(self.description)
        self.available = encryptData(self.available)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def fkToDict(self):
        helper = {}
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.description = decryptData(data.description)
        data.available = decryptData(data.available)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.description = decryptData(item.description)
            item.available = decryptData(item.available)
        return data


class Degree(Model):
    __tablename__ = 'degree'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False, info={'label': 'Degree Name'})
    description = Column(Unicode(250), nullable=False, info={'label': 'Degree Description'})
    active = Column(Unicode(250), index=True, server_default=text("((1))"))

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.description = encryptData(self.description)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.description = decryptData(data.description)
        data.active = (True) if decryptData(data.active) == '1' else False
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.description = decryptData(item.description)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class Equipment(Model):
    __tablename__ = 'equipment'
    __table_args__ = (
        Index('unique_equipment', 'name', 'brand', 'model', 'serial', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False)
    brand = Column(Unicode(250), nullable=False)
    model = Column(Unicode(250), nullable=False)
    serial = Column(Unicode(250), nullable=False, unique=True)
    active = Column(Unicode(250), index=True, server_default=text("((1))"))

    experiments = relationship('Experiment', secondary='experiment_equipment')

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.brand = encryptData(self.brand)
        self.model = encryptData(self.model)
        self.serial = encryptData(self.serial)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.brand = decryptData(data.brand)
        data.model = decryptData(data.model)
        data.serial = decryptData(data.serial)
        data.active = decryptData(data.active)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.brand = decryptData(item.brand)
            item.model = decryptData(item.model)
            item.serial = decryptData(item.serial)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class TableRef(Model):
    __tablename__ = 'table_ref'

    name = Column(Unicode(250), primary_key=True, autoincrement=False)
    description = Column(Unicode(250), nullable=False, unique=True)
    current_value = Column(Unicode(250), server_default=text("((0))"))
    isHidden = Column(Unicode(250), server_default=text("((0))"))
    available = Column(Unicode(250), server_default=text("((1))"))

    @classmethod
    def getNextID(cls, tableName):
        newID = db.session.query(cls).get(tableName)
        newID.current_value += 1
        db.session.commit()
        return newID.current_value - 1

    def save(self):
        db.session.add(self)
        db.session.commit()


class UserRole(Model):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False, unique=True, info={'label': 'User Role Name'})
    description = Column(Unicode(250), nullable=False, info={'label': 'User Role Description'})
    active = Column(Unicode(250), index=True, server_default=text("((1))"))

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.description = encryptData(self.description)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.description = decryptData(data.description)
        data.active = decryptData(data.active)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.description = decryptData(item.description)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class Consecutive(Model):
    __tablename__ = 'consecutive'

    id = Column(Integer, primary_key=True,  autoincrement=False)
    type_id = Column(ForeignKey('code.id'), nullable=False, unique=True)
    description = Column(Unicode(250), nullable=False, info={'label': 'Consecutive Description'})
    value = Column(Unicode(250), server_default=text("((0))"), info={'label': 'Consecutive Value'})
    prefix = Column(Unicode(250), info={'label': 'Consecutive Prefix'})
    table_name_id = Column(ForeignKey('table_ref.name'), nullable=False, unique=True)
    table_name = relationship('TableRef')
    type = relationship('Code')

    def save(self):
        self.description = encryptData(self.description)
        self.value = self.value
        self.prefix = encryptData(self.prefix)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def fkToDict(self):
        helper = {}
        helper.update({'table_name_id': self.table_name})
        helper.update({'type_id': self.type})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.description = decryptData(data.description)
        data.value = decryptData(data.value)
        data.prefix = decryptData(data.prefix)
        data.table_name = TableRef.query.get(data.table_name_id)
        data.type = Code.getByID(data.type_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.description = decryptData(item.description)
            item.value = decryptData(item.value)
            item.prefix = decryptData(item.prefix)
        return data


class Job(Model):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False, unique=True, info={'label': 'Job Name'})
    active = Column(Unicode(250), nullable=True, index=True, server_default=text("((1))"))
    user_role_id = Column(ForeignKey('user_role.id'), nullable=False)
    user_role = relationship('UserRole')

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'user_role_id': self.user_role})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.active = decryptData(data.active)
        data.user_role = UserRole.getByID(data.user_role_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class Person(UserMixin, Model):
    __tablename__ = 'person'
    __table_args__ = (
        Index('unique_fullname_person', 'name', 'firstSurname', 'secondSurname', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    nickname = Column(Unicode(250), nullable=False, unique=True, info={'label': 'Nickname'})
    # noinspection PyDeprecation
    password = Column(Unicode(500), nullable=True,  info={'label': 'Password'})
    isAdmin = Column(Unicode(250), nullable=False, server_default=text("((0))"),  info={'label': 'User Rights'})
    active = Column(Unicode(250), nullable=False, index=True, server_default=text("((1))"))
    name = Column(Unicode(250), nullable=False, info={'label': 'First Name'})
    firstSurname = Column(Unicode(250), nullable=False,  info={'label': 'Surname 1'})
    secondSurname = Column(Unicode(250), nullable=True,  info={'label': 'Surname 2'})
    phone = Column(Unicode(250), nullable=False, info={'label': 'Phone Number'})
    signature = Column(Unicode(300))
    photo = Column(Unicode(300))
    degree_id = Column(Integer, ForeignKey('degree.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    degree = relationship('Degree')
    job = relationship('Job')

    def set_password(self, password):
        """Create hashed password."""
        if not isinstance(password,str):
            password = str(password)
        self.password = generate_password_hash(
            password,
            method='sha256'
        )
        p = self.password

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.nickname = encryptData(self.nickname)
        self.isAdmin = encryptData('1' if self.isAdmin else '0')
        self.active = encryptData(self.active)
        self.name = encryptData(self.name)
        self.firstSurname = encryptData(self.firstSurname)
        self.secondSurname = encryptData(self.secondSurname)
        self.phone = encryptData(self.phone)
        if self.password and self.password != '':
            self.set_password(self.password)
        if self.signature is not None:
            self.signature = encryptData(self.signature)
        if self.photo is not None:
            self.photo = encryptData(self.photo)
        db.session.add(self)
        if self.degree is not None:
            self.degree.save()
        if self.job is not None:
            self.job.save()
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'degree_id': self.degree})
        helper.update({'job_id': self.job})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        if data is not None:
            data.nickname = decryptData(data.nickname)
            data.isAdmin = decryptData(data.isAdmin)
            data.name = decryptData(data.name)
            data.firstSurname = decryptData(data.firstSurname)
            data.secondSurname = decryptData(data.secondSurname)
            data.phone = decryptData(data.phone)
            data.signature = decryptData(data.signature) if data.signature is not None else None
            data.photo = decryptData(data.photo) if data.photo is not None else None
            data.active = decryptData(data.active)
            data.degree = Degree.getByID(data.degree_id)
            data.job = Job.getByID(data.job_id)
        else:
            return None
        return data if data.active == '1' else None

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.nickname = decryptData(item.nickname)
            item.isAdmin = decryptData(item.isAdmin)
            item.active = decryptData(item.active)
            item.name = decryptData(item.name)
            item.firstSurname = decryptData(item.firstSurname)
            item.secondSurname = decryptData(item.secondSurname)
            item.phone = decryptData(item.phone)
            item.degree = Degree.getByID(item.degree_id)
            item.job = Job.getByID(item.job_id)
            item.signature = decryptData(item.signature) if item.signature is not None else None
            item.photo = decryptData(item.photo) if item.photo is not None else None
        data = list(filter(lambda x: x.active == '1', data))
        return data

    @classmethod
    def getByNickname(cls, userInput):
        data = Person.getByAll()
        data = list(filter(lambda x: x.nickname == userInput, data))
        return data[0] if len(data) > 0 else None


class ActivityLog(Model):
    __tablename__ = 'activity_log'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    table_name_id = Column(ForeignKey('table_ref.name'), primary_key=True, nullable=False)
    person_id = Column(ForeignKey('person.id'), nullable=False, index=True)
    date_time = Column(Unicode(250), server_default=text("(getdate())"))
    description = Column(Unicode(250), nullable=False)
    person = relationship('Person')
    table_name = relationship('TableRef')

    def save(self):
        self.date_time = encryptData(str(self.date_time))
        self.description = encryptData(self.description)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def fkToDict(self):
        helper = {}
        helper.update({'table_name_id': self.table_name})
        helper.update({'person_id': self.person})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.date_time = decryptData(data.date_time)
        data.description = decryptData(data.description)
        data.table_name = TableRef.query.get(data.table_name_id)
        data.person = Person.getByID(data.person_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.date_time = decryptData(item.date_time)
            item.description = decryptData(item.description)
        return data


class ErrorLog(Model):
    __tablename__ = 'error_log'
    __table_args__ = (
        Index('unique_person_error_record', 'person_id', 'date_time', 'table_name_id', unique=True),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    person_id = Column(ForeignKey('person.id'), nullable=False, index=True)
    date_time = Column(Unicode(250), server_default=text("(getdate())"))
    table_name_id = Column(ForeignKey('table_ref.name'), primary_key=True, nullable=False)
    description = Column(Unicode(250), nullable=False)
    summary = Column(Unicode(2000), nullable=False)
    person = relationship('Person')
    table_name = relationship('TableRef')

    def save(self):
        self.date_time = encryptData(str(self.date_time))
        self.description = encryptData(self.description)
        self.summary = encryptData(self.summary)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def fkToDict(self):
        helper = {}
        helper.update({'person_id': self.person})
        helper.update({'table_name_id': self.table_name})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.date_time = decryptData(data.date_time)
        data.description = decryptData(data.description)
        data.summary = decryptData(data.summary)
        data.person = Person.getByID(data.person_id)
        data.table_name = TableRef.query.get(data.table_name_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.date_time = decryptData(item.date_time)
            item.description = decryptData(item.description)
            item.summary = decryptData(item.summary)
        return data


class Project(Model):
    __tablename__ = 'project'
    __table_args__ = (
        Index('INDXPROJECT', 'person_id', 'active'),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False)
    price = Column(Unicode(250), server_default=text("((0))"))
    journals = Column(Unicode(250), server_default=text("((0))"))
    active = Column(Unicode(250), server_default=text("((1))"))
    person_id = Column(ForeignKey('person.id'), nullable=False)
    branch_id = Column(ForeignKey('branch.id'), nullable=False)
    branch = relationship('Branch')
    person = relationship('Person')

    def __init__(self):
        super().__init__()
        self.price = '0'
        self.journals = '0'
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.price = encryptData(self.price)
        self.active = encryptData(self.active)
        self.journals = encryptData(self.journals)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'person_id': self.person})
        helper.update({'branch_id': self.branch})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.price = decryptData(data.price)
        data.active = decryptData(data.active)
        data.journals = decryptData(data.journals)
        data.person = Person.getByID(data.person_id)
        data.branch = Branch.getByID(data.branch_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.price = decryptData(item.price)
            item.active = decryptData(item.active)
            item.journals = decryptData(item.journals)
            item.person = Person.getByID(item.person_id)
            item.branch = Branch.getByID(item.branch_id)
        data = list(filter(lambda x: x.active == '1', data))
        return data

    @classmethod
    def getAllFull(cls, args):
        data = db.session.query(Project, func.count(Experiment.id).label('experiments'), Branch.name).select_from(Project).join(Experiment, Branch).group_by(Project, Branch.name)
        if 'branch' in args:
            data = data.filter(Branch.id == args.get('branch'))
        if 'owner' in args:
            data = data.filter(Project.person_id == args.get('owner'))
        if 'id' in args:
            data = data.filter(Project.id == args.get('id'))
        data = data.all()
        data = copy.deepcopy(data)
        auxArray = []
        for row in data:
            headers = row.keys()
            values = list(row)
            auxDict = dict(zip(headers, values))
            row = auxDict.get('Project')
            row.name = decryptData(row.name)
            row.price = int(decryptData(row.price))
            row.active = decryptData(row.active)
            row.branch = decryptData(auxDict.get('name'))
            row.journals = auxDict.get('experiments')
            row.person = Person.getByID(row.person_id)
            row.person = f'{row.person.firstSurname} {row.person.secondSurname}, {row.person.name}'
            auxArray.append(row)

        data = list(filter(lambda x: x.active == '1', auxArray))
        if len(data) > 0:
            if 'gt' in args:
                data = list(filter(lambda x: x.price >= int(args.get('gt')), auxArray))
            elif 'lt' in args:
                data = list(filter(lambda x: x.price <= int(args.get('lt')), auxArray))
        return data


class Experiment(Model):
    __tablename__ = 'experiment'
    __table_args__ = (
        Index('INDXEXPERIMENT', 'project_id', 'active'),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(250), nullable=False, info={'label': 'Experiment Name'})
    date = Column(Unicode(250), server_default=text("(getdate())"), info={'label': 'Experiment Date'})
    description = Column(Unicode(2000), nullable=False, info={'label': 'Description'})
    main_objective = Column(Unicode(3000), nullable=False, info={'label': 'Main Objective'})
    active = Column(Unicode(250), server_default=text("((1))"))
    project_id = Column(ForeignKey('project.id'), nullable=False)
    experimenter_id = Column(ForeignKey('person.id'))
    witness_id = Column(ForeignKey('person.id'))

    experimenter = relationship('Person', primaryjoin='Experiment.experimenter_id == Person.id')
    project = relationship('Project')
    witness = relationship('Person', primaryjoin='Experiment.witness_id == Person.id')

    # Adding methodology relationship
    methodology = relationship('Methodology',  back_populates="experiment")
    equipments = relationship(Equipment, secondary='experiment_equipment')

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.name = encryptData(self.name)
        self.date = encryptData(self.date)
        self.description = encryptData(self.description)
        self.main_objective = encryptData(self.main_objective)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'project_id': self.project})
        helper.update({'experimenter_id': self.experimenter})
        helper.update({'witness_id': self.witness})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.name = decryptData(data.name)
        data.date = decryptData(data.date)
        data.description = decryptData(data.description)
        data.main_objective = decryptData(data.main_objective)
        data.active = decryptData(data.active)
        data.project = Project.getByID(data.project_id)
        data.experimenter = Person.getByID(data.experimenter_id)
        data.witness = Person.getByID(data.witness_id)
        return data

    @classmethod
    def getByAll(cls, pk=None):
        data = cls.query
        if pk is not None:
            data = data.filter(cls.project_id == pk)
        data = data.all()
        methodology = {}
        equipment = {}
        for item in data:
            methodologyParents = []
            equipmentParents = []
            for parent in item.methodology:
                child = Methodology.getByID(parent.id)
                if child.active == '1':
                    methodologyParents.append(child)

            for parent in item.equipments:
                child = Equipment.getByID(parent.id)
                if child.active == '1':
                    equipmentParents.append(child)

            methodology.update({item.id:methodologyParents})
            equipment.update({item.id: equipmentParents})

        data = copy.deepcopy(data)
        for item in data:
            item.name = decryptData(item.name)
            item.date = decryptData(item.date)
            item.description = decryptData(item.description)
            item.main_objective = decryptData(item.main_objective)
            item.active = decryptData(item.active)
            item.experimenter = Person.getByID(item.experimenter_id)
            item.witness = Person.getByID(item.experimenter_id)
        data = list(filter(lambda x: x.active == '1', data))
        return data, methodology, equipment


class ExperimentImage(Model):
    __tablename__ = 'experiment_image'
    __table_args__ = (
        Index('INDXEXPIMG', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    photo = Column(Unicode(300))
    active = Column(Unicode(250), server_default=text("((1))"))
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)

    experiment = relationship('Experiment')

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.photo = encryptData(self.photo)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'experiment_id': self.experiment})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.photo = decryptData(data.photo)
        data.active = decryptData(data.active)
        data.experiment = Experiment.getByID(data.experiment_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.name = decryptData(item.name)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data

    @classmethod
    def getByExperimentID(cls, pk):
        data = ExperimentImage.getByAll()
        results = list(filter(lambda x: x["experiment_id"] == pk, data))
        return results


class Methodology(Model):
    __tablename__ = 'methodology'
    __table_args__ = (
        Index('INDXMETHODOLOGY', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    step = Column(Unicode(250), nullable=False)
    description = Column(Unicode(1000), nullable=False)
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)
    active = Column(Unicode(250), server_default=text("((1))"))

    experiment = relationship('Experiment', back_populates="methodology")

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.step = encryptData(self.step)
        self.description = encryptData(self.description)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'experiment_id': self.experiment})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.step = decryptData(data.step)
        data.description = decryptData(data.description)
        data.active = decryptData(data.active)
        data.experiment = Experiment.getByID(data.experiment_id)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.step = decryptData(item.step)
            item.description = decryptData(item.description)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data

    @classmethod
    def getByExperimentID(cls, pk):
        data = Methodology.getByAll()
        data = list(filter(lambda x: x.experiment_id == int(pk), data))
        return data


class Objective(Model):
    __tablename__ = 'objective'
    __table_args__ = (
        Index('INDXOBJECTIVE', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True, autoincrement=False)
    description = Column(Unicode(250), nullable=False)
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)
    active = Column(Unicode(250), server_default=text("((1))"))

    experiment = relationship('Experiment')

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.description = encryptData(self.description)
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'experiment_id': self.experiment})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls).get(pk))
        data.description = decryptData(data.description)
        data.active = decryptData(data.active)
        return data

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls).all())
        for item in data:
            item.description = decryptData(item.description)
            item.active = decryptData(item.active)
        data = list(filter(lambda x: x.active == '1', data))
        return data


class ExperimentEquipment(Model):
    __tablename__ = 'experiment_equipment'
    experiment_id = Column(Integer, ForeignKey('experiment.id'), primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), primary_key=True)
    active = Column(Integer)
    experiment = relationship(Experiment, backref=backref('experiment_assoc'))
    equipment = relationship(Equipment, backref=backref('equipment_assoc'))

    def __init__(self):
        super().__init__()
        self.active = '1'

    def save(self):
        self.active = encryptData(self.active)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.active = '0'
        self.save()

    def fkToDict(self):
        helper = {}
        helper.update({'experiment_id': self.experiment})
        helper.update({'equipment_id': self.equipment})
        return helper

    @classmethod
    def getByID(cls, pk):
        data = copy.deepcopy(db.session.query(cls, Equipment).join(Equipment).filter(Equipment.id == pk).all())
        results = []
        for item in data:
            helper = {}
            helper.update({"brand": decryptData(item.Equipment.brand)})
            helper.update({"name": decryptData(item.Equipment.name)})
            helper.update({"serial": decryptData(item.Equipment.serial)})
            helper.update({"model": decryptData(item.Equipment.model)})
            helper.update({"active": decryptData(item.ExperimentEquipment.active)})
            helper.update({"experiment_id": item.ExperimentEquipment.experiment_id})
            helper.update({"equipment_id": item.ExperimentEquipment.equipment_id})
            helper.update({"experiment": Experiment.getByID(item.ExperimentEquipment.experiment_id)})
            helper.update({"equipment": Equipment.getByID(item.ExperimentEquipment.equipment_id)})
            results.append(helper)
        results = list(filter(lambda x: x["active"] == '1', results))
        return results

    @classmethod
    def getByAll(cls):
        data = copy.deepcopy(db.session.query(cls, Equipment).join(Equipment).all())
        results = []
        for item in data:
            helper = {}
            helper.update({"id": item.Equipment.id})
            helper.update({"brand": decryptData(item.Equipment.brand)})
            helper.update({"name": decryptData(item.Equipment.name)})
            helper.update({"model": decryptData(item.Equipment.model)})
            helper.update({"active": decryptData(item.ExperimentEquipment.active)})
            helper.update({"experiment_id": item.ExperimentEquipment.experiment_id})
            helper.update({"equipment_id": item.ExperimentEquipment.equipment_id})
            results.append(helper)
        results = list(filter(lambda x: x["active"] == '1', results))
        return results

    @classmethod
    def getByExperimentID(cls, pk):
        data = ExperimentEquipment.getByAll()
        results = list(filter(lambda x: x["experiment_id"] == int(pk), data))
        return results

# t_experiment_equipment = Table(
#     'experiment_equipment', metadata,
#     Column('experiment_id', ForeignKey('experiment.id'), nullable=False),
#     Column('equipment_id', ForeignKey('equipment.id'), nullable=False),
#     Column('active', Integer, index=True, server_default=text("((1))"))
# )

t_view_activity_log = Table(
    'view_activity_log', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('table_name', Unicode(250)),
    Column('person', Unicode(250)),
    Column('date_time', DateTime),
    Column('description', Unicode(250), nullable=False),
    Column('active', Unicode(250), nullable=False)
)


t_view_branch = Table(
    'view_branch', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('active', Unicode(250), nullable=False)
)


t_view_degree = Table(
    'view_degree', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('description', Unicode(250), nullable=False),
    Column('active', Unicode(250), nullable=False)
)


t_view_error_log = Table(
    'view_error_log', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('person', Unicode(250)),
    Column('date_time', DateTime),
    Column('table_name', Unicode(250)),
    Column('description', Unicode(200), nullable=False),
    Column('summary', Unicode(2000), nullable=False),
    Column('active', Unicode(250), nullable=False)
)


t_view_experiment = Table(
    'view_experiment', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('date', Unicode(250)),
    Column('description', Unicode(2000), nullable=False),
    Column('main_objective', Unicode(3000), nullable=False),
    Column('project', Unicode(250)),
    Column('active', Unicode(250), nullable=False)
)


t_view_job = Table(
    'view_job', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('role', Unicode(250)),
    Column('active', Unicode(250), nullable=False)
)


t_view_person = Table(
    'view_person', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('nickname', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('firstSurname', Unicode(250), nullable=False),
    Column('secod_surname', Unicode(250), nullable=False),
    Column('phone', Unicode(250), nullable=False),
    Column('signature', Unicode(250)),
    Column('photo', Unicode(250)),
    Column('degree', Unicode(250)),
    Column('job', Unicode(250)),
    Column('active', Unicode(250), nullable=False)
)


t_view_project = Table(
    'view_project', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('price', Unicode(250)),
    Column('branch', Unicode(250)),
    Column('active', Unicode(250), nullable=False)
)


t_view_user_role = Table(
    'view_user_role', metadata,
    Column('id', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False),
    Column('value', Unicode(250), nullable=False),
    Column('name', Unicode(250), nullable=False),
    Column('description', Unicode(100), nullable=False),
    Column('active', Unicode(250), nullable=False)
)

t_view_code = Table(
    'view_code', metadata,
    Column('id', Integer, nullable=False),
    Column('description', Unicode(250), nullable=False)
)

t_view_consecutive = Table(
    'view_consecutive', metadata,
    Column('id', Integer, nullable=False),
    Column('type', Unicode(250), nullable=False),
    Column('description', Unicode(100), nullable=False),
    Column('value', Integer, nullable=False),
    Column('prefix', Unicode(250), nullable=False)
)
