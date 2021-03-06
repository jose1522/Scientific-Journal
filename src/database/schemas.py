from . import ma
from .models import *
from marshmallow import fields, Schema


# class PersonSchema(ma.Schema):
#     class Meta:
#         fields = ('nickname','name','firstsurname','lastsurname','isadmin','job.name','degree.name','link')
#     link = ma.Hyperlinks({"self": ma.URLFor("admin.userCRUD", id="<id>")})

# class PersonSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = Person
#         ordered = True
#
#     link = ma.Hyperlinks(ma.URLFor("admin.userCRUD", id="<id>"))
#     name = ma.auto_field(data_key='First Name')
#     firstSurname = ma.auto_field(data_key='First Surname')
#     secondSurname = ma.auto_field(data_key='Second Surname')
#     job = fields.Pluck("self","name",data_key='Job Title')

class DegreeSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="degree"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='Name')
    description = fields.Str(data_key='Description')


class DegreeSchemaFull(Schema):
    class Meta:
        ordered = True

    name = fields.Str(data_key='Name')
    description = fields.Str(data_key='Description')


class MethodologySchemaFull(Schema):
    class Meta:
        ordered = True

    step = fields.Str(data_key='Step')
    description = fields.Str(data_key='Description')
    experiment_id = fields.Str(data_key='Experiment')


class EquipmentSchemaFull(Schema):
    class Meta:
        ordered = True

    name = fields.Str(data_key='Name')
    brand = fields.Str(data_key='Brand')
    model = fields.Str(data_key='Model')
    serial = fields.Str(data_key='Serial')


class JobSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="job"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='First Name')


class JobSchemaFull(ma.SQLAlchemyAutoSchema):
    class Meta:
        ordered = True

    name = fields.Str(data_key='First Name')

class PersonSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.userCRUD", id="<id>"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='First Name')
    firstSurname = fields.Str(data_key='First Surname')
    secondSurname = fields.Str(data_key='Second Surname')
    job = fields.Str(data_key='Job Title')


class PersonSchemaFull(Schema):
    class Meta:
        ordered = True

    name = fields.Str(data_key='First Name')
    firstSurname = fields.Str(data_key='First Surname')
    secondSurname = fields.Str(data_key='Second Surname')
    job = fields.Nested(JobSchemaFull)
    degree = fields.Nested(DegreeSchemaFull)


class ProjectSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="project"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='Name')
    person = fields.Str(data_key='Owner')
    branch = fields.Str(data_key='Branch')


class ProjectSchemaFull(Schema):
    class Meta:
        ordered = True

    id = fields.Str(data_key='ID')
    name = fields.Str(data_key='Name')
    price = fields.Str(data_key='Price')
    person = fields.Str(data_key='Person')
    branch = fields.Str(data_key='Branch')


class BranchSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="branch"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='Name')

class BranchSchemaFull(Schema):
    class Meta:
        ordered = True

    id = fields.Str(data_key='id')
    name = fields.Str(data_key='Name')

class CodeSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="code"))
    description = fields.Str(data_key='Description')


class ConsecutiveSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="consecutive"))
    type = fields.Str(data_key='Type')
    description = fields.Str(data_key='Description')
    value = fields.Str(data_key='Starting Number')
    prefix = fields.Str(data_key='Prefix')


class RoleSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.formCRUD", id="<id>", name="user-role"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='Name')
    description = fields.Str(data_key='Description')


class ActivitySchema(Schema):
    class Meta:
        ordered = True

    code = fields.Str(data_key='Code')
    person = fields.Str(data_key='Name')
    date_time = fields.Str(data_key='Date')
    table_name = fields.Str(data_key='Table')
    description = fields.Str(data_key='Description')


class ErrorSchema(Schema):
    class Meta:
        ordered = True

    code = fields.Str(data_key='Code')
    person = fields.Str(data_key='Name')
    date_time = fields.Str(data_key='Date')
    table_name = fields.Str(data_key='Table')
    description = fields.Str(data_key='Description')
    summary = fields.Str(data_key='Summary')


class ExperimentSchema(Schema):
    class Meta:
        ordered = True

    link = ma.Hyperlinks(ma.URLFor("admin.experimentCRUD", id="<id>"))
    code = fields.Str(data_key='Code')
    name = fields.Str(data_key='Name')
    project = fields.Str(data_key='Project')
    experimenter = fields.Str(data_key='Owner')


class ExperimentSchemaFull(Schema):
    class Meta:
        ordered = True

    id = fields.Str(data_key='ID')
    name = fields.Str(data_key='Name')
    date = fields.Str(data_key='Date')
    description = fields.Str(data_key='Description')
    main_objective = fields.Str(data_key='Objective')
    experimenter = fields.Nested(PersonSchemaFull)
    witness = fields.Nested(PersonSchemaFull)