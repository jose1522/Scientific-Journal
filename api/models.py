# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.mssql import BIT, IMAGE
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Degree(Base):
    __tablename__ = 'degree'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    active = Column(BIT, server_default=text("((1))"))


class Equipment(Base):
    __tablename__ = 'equipment'
    __table_args__ = (
        Index('unique_equipment', 'name', 'brand', 'model', 'serial', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    brand = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    model = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    serial = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    active = Column(BIT, server_default=text("((1))"))


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    description = Column(String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    active = Column(BIT, server_default=text("((1))"))


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    description = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    active = Column(BIT, nullable=False, server_default=text("((1))"))
    user_role = Column(ForeignKey('user_role.id'), nullable=False)

    user_role1 = relationship('UserRole')


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        Index('unique_fullname_person', 'name', 'first_surname', 'second_surname', unique=True),
    )

    id = Column(Integer, primary_key=True)
    nickname = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    password = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    active = Column(BIT, nullable=False, server_default=text("((1))"))
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    first_surname = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    second_surname = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    phone = Column(Integer, nullable=False, unique=True)
    signature = Column(IMAGE)
    photo = Column(IMAGE)
    degree = Column(ForeignKey('degree.id'), nullable=False)
    job = Column(ForeignKey('job.id'), nullable=False)

    degree1 = relationship('Degree')
    job1 = relationship('Job')


class ErrorLog(Base):
    __tablename__ = 'error_log'
    __table_args__ = (
        Index('unique_person_error_record', 'person', 'date_time', 'table_name', unique=True),
    )

    id = Column(Integer, primary_key=True)
    person = Column(ForeignKey('person.id'), nullable=False)
    date_time = Column(DateTime, server_default=text("(getdate())"))
    table_name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    description = Column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    summary = Column(String(2000, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    person1 = relationship('Person')


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, unique=True)
    price = Column(Float(53), server_default=text("((0))"))
    journals = Column(Integer, server_default=text("((0))"))
    active = Column(BIT, server_default=text("((1))"))
    person = Column(ForeignKey('person.id'), nullable=False)

    person1 = relationship('Person')


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    date = Column(Date, server_default=text("(getdate())"))
    description = Column(String(2000, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    main_objective = Column(String(3000, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    project = Column(ForeignKey('project.id'), nullable=False)

    project1 = relationship('Project')
