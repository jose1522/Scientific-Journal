# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, Table, Unicode, text
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

Base = db
Model = Base.Model
metadata = Base.metadata

class Branch(Model):
    __tablename__ = 'branch'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    active = Column(Integer, index=True, server_default=text("((1))"))


class Code(Model):
    __tablename__ = 'code'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(50), nullable=False, unique=True, info={'label': 'Code Description'})
    available = Column(Integer, server_default=text("((1))"))

    def __repr__(self):
        return str([{"id":self.id},{"description":self.description}])


class Degree(Model):
    __tablename__ = 'degree'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False, info={'label': 'Degree Name'})
    description = Column(Unicode(50), nullable=False, info={'label': 'Degree Description'})
    active = Column(Integer, index=True, server_default=text("((1))"))


class Equipment(Model):
    __tablename__ = 'equipment'
    __table_args__ = (
        Index('unique_equipment', 'name', 'brand', 'model', 'serial', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    brand = Column(Unicode(50), nullable=False)
    model = Column(Unicode(50), nullable=False)
    serial = Column(Unicode(50), nullable=False, unique=True)
    active = Column(Integer, index=True, server_default=text("((1))"))


class TableRef(Model):
    __tablename__ = 'table_ref'

    name = Column(Unicode(50), primary_key=True)
    description = Column(Unicode(50), nullable=False, unique=True)
    current_value = Column(Integer, server_default=text("((0))"))
    isHidden = Column(Integer, server_default=text("((0))"))
    available = Column(Integer, server_default=text("((1))"))

    def __repr__(self):
        # easy to override, and it'll honor __repr__ in foreign relationships
        return str([{"name":self.name},{"description":self.description}])

class UserRole(Model):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False, unique=True, info={'label': 'User Role Name'})
    description = Column(Unicode(100), nullable=False, info={'label': 'User Role Description'})
    active = Column(Integer, index=True, server_default=text("((1))"))

    def __repr__(self):
        return str([{'id':self.id},{'name':self.name}])


class Consecutive(Model):
    __tablename__ = 'consecutive'

    id = Column(Integer, primary_key=True)
    type_id = Column(ForeignKey('code.id'), nullable=False, unique=True)
    description = Column(Unicode(100), nullable=False, info={'label': 'Consecutive Description'})
    value = Column(Integer, server_default=text("((0))"), info={'label': 'Consecutive Value'})
    prefix = Column(Unicode(50), info={'label': 'Consecutive Prefix'})
    table_name_id = Column(ForeignKey('table_ref.name'), nullable=False, unique=True)
    table_name = relationship('TableRef')
    type = relationship('Code')


class Job(Model):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False, unique=True, info={'label': 'Job Name'})
    active = Column(Integer, nullable=True, index=True, server_default=text("((1))"))
    user_role_id = Column(ForeignKey('user_role.id'), nullable=False)
    user_role = relationship('UserRole')

    def __repr__(self):
        return str([{'id',self.id},{'name': self.name}])


class Person(UserMixin, Model):
    __tablename__ = 'person'
    __table_args__ = (
        Index('unique_fullname_person', 'name', 'firstSurname', 'secondSurname', unique=True),
    )

    id = Column(Integer, primary_key=True)
    nickname = Column(Unicode(50), nullable=False, unique=True, info={'label': 'Nickname'})
    # noinspection PyDeprecation
    password = Column(Unicode(500), nullable=True,  info={'label': 'Password'})
    isAdmin = Column(Integer, nullable=False, server_default=text("((0))"),  info={'label': 'User Rights'})
    active = Column(Integer, nullable=False, index=True, server_default=text("((1))"))
    name = Column(Unicode(50), nullable=False, info={'label': 'First Name'})
    firstSurname = Column(Unicode(50), nullable=False,  info={'label': 'Surname 1'})
    secondSurname = Column(Unicode(50), nullable=True,  info={'label': 'Surname 2'})
    phone = Column(Integer, nullable=False, info={'label': 'Phone Number'})
    signature = Column(Unicode(300))
    photo = Column(Unicode(300))
    degree_id = Column(Integer, ForeignKey('degree.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    degree = relationship('Degree')
    job = relationship('Job')

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)


class ActivityLog(Model):
    __tablename__ = 'activity_log'

    id = Column(Integer, primary_key=True, nullable=False)
    table_name_id = Column(ForeignKey('table_ref.name'), primary_key=True, nullable=False)
    person_id = Column(ForeignKey('person.id'), nullable=False, index=True)
    date_time = Column(DateTime, server_default=text("(getdate())"))
    description = Column(Unicode(200), nullable=False)
    person = relationship('Person')
    table_name = relationship('TableRef')


class ErrorLog(Model):
    __tablename__ = 'error_log'
    __table_args__ = (
        Index('unique_person_error_record', 'person_id', 'date_time', 'table_name_id', unique=True),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    person_id = Column(ForeignKey('person.id'), nullable=False, index=True)
    date_time = Column(DateTime, server_default=text("(getdate())"))
    table_name_id = Column(ForeignKey('table_ref.name'), primary_key=True, nullable=False)
    description = Column(Unicode(200), nullable=False)
    summary = Column(Unicode(2000), nullable=False)
    person = relationship('Person')
    table_name = relationship('TableRef')


class Project(Model):
    __tablename__ = 'project'
    __table_args__ = (
        Index('INDXPROJECT', 'person_id', 'active'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    price = Column(Float(53), server_default=text("((0))"))
    journals = Column(Integer, server_default=text("((0))"))
    active = Column(Integer, server_default=text("((1))"))
    person_id = Column(ForeignKey('person.id'), nullable=False)
    branch_id = Column(ForeignKey('branch.id'), nullable=False)
    branch = relationship('Branch')
    person = relationship('Person')


class Experiment(Model):
    __tablename__ = 'experiment'
    __table_args__ = (
        Index('INDXEXPERIMENT', 'project_id', 'active'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False, info={'label': 'Experiment Name'})
    date = Column(Date, server_default=text("(getdate())"), info={'label': 'Experiment Date'})
    description = Column(Unicode(2000), nullable=False, info={'label': 'Description'})
    main_objective = Column(Unicode(3000), nullable=False, info={'label': 'Main Objective'})
    active = Column(Integer, server_default=text("((1))"))
    project_id = Column(ForeignKey('project.id'), nullable=False)
    experimenter_id = Column(ForeignKey('person.id'))
    witness_id = Column(ForeignKey('person.id'))

    experimenter = relationship('Person', primaryjoin='Experiment.experimenter_id == Person.id')
    project = relationship('Project')
    witness = relationship('Person', primaryjoin='Experiment.witness_id == Person.id')

    # Adding methodology relationship
    methodology = relationship('Methodology',  back_populates="experiment")

t_experiment_equipment = Table(
    'experiment_equipment', metadata,
    Column('experiment_id', ForeignKey('experiment.id'), nullable=False),
    Column('equipment_id', ForeignKey('equipment.id'), nullable=False),
    Column('active', Integer, index=True, server_default=text("((1))"))
)

class ExperimentImage(Model):
    __tablename__ = 'experiment_image'
    __table_args__ = (
        Index('INDXEXPIMG', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True)
    photo = Column(Unicode(300))
    active = Column(Integer, server_default=text("((1))"))
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)

    experiment = relationship('Experiment')

class Methodology(Model):
    __tablename__ = 'methodology'
    __table_args__ = (
        Index('INDXMETHODOLOGY', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True)
    step = Column(Integer, nullable=False)
    description = Column(Unicode(1000), nullable=False)
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)
    active = Column(Integer, server_default=text("((1))"))

    experiment = relationship('Experiment', back_populates="methodology")


class Objective(Model):
    __tablename__ = 'objective'
    __table_args__ = (
        Index('INDXOBJECTIVE', 'experiment_id', 'active'),
    )

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(50), nullable=False)
    experiment_id = Column(ForeignKey('experiment.id'), nullable=False)
    active = Column(Integer, server_default=text("((1))"))

    experiment = relationship('Experiment')

t_view_activity_log = Table(
    'view_activity_log', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('table_name', Unicode(50)),
    Column('person', Unicode(50)),
    Column('date_time', DateTime),
    Column('description', Unicode(200), nullable=False)
)


t_view_branch = Table(
    'view_branch', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False)
)


t_view_degree = Table(
    'view_degree', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('description', Unicode(50), nullable=False)
)


t_view_error_log = Table(
    'view_error_log', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('person', Unicode(50)),
    Column('date_time', DateTime),
    Column('table_name', Unicode(50)),
    Column('description', Unicode(200), nullable=False),
    Column('summary', Unicode(2000), nullable=False)
)


t_view_experiment = Table(
    'view_experiment', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('date', Date),
    Column('description', Unicode(2000), nullable=False),
    Column('main_objective', Unicode(3000), nullable=False),
    Column('project', Unicode(50)),
    Column('experimenter', Unicode(153), nullable=False),
    Column('withness', Unicode(153), nullable=False),
    Column('equipment', Unicode(4000)),
    Column('methodology', Unicode(4000)),
    Column('objective', Unicode(4000))
)


t_view_job = Table(
    'view_job', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('role', Unicode(50))
)


t_view_person = Table(
    'view_person', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('nickname', Unicode(50), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('firstSurname', Unicode(50), nullable=False),
    Column('secod_surname', Unicode(50), nullable=False),
    Column('phone', Integer, nullable=False),
    Column('signature', LargeBinary),
    Column('photo', LargeBinary),
    Column('degree', Unicode(50)),
    Column('job', Unicode(50))
)


t_view_project = Table(
    'view_project', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('price', Float(53)),
    Column('journals', Integer),
    Column('person', Unicode(153), nullable=False),
    Column('branch', Unicode(50))
)


t_view_user_role = Table(
    'view_user_role', metadata,
    Column('id', Integer, nullable=False),
    Column('code', Unicode(62), nullable=False),
    Column('name', Unicode(50), nullable=False),
    Column('description', Unicode(100), nullable=False)
)

t_view_code = Table(
    'view_code', metadata,
    Column('id', Integer, nullable=False),
    Column('description', Unicode(50), nullable=False)
)

t_view_consecutive = Table(
    'view_consecutive', metadata,
    Column('id', Integer, nullable=False),
    Column('type', Unicode(50), nullable=False),
    Column('description', Unicode(100), nullable=False),
    Column('value', Integer, nullable=False),
    Column('prefix', Unicode(50), nullable=False)
)