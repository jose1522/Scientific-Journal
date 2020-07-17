from . import ma
from .models import *
from marshmallow import fields, Schema
# class PersonSchema(ma.Schema):
#     class Meta:
#         fields = ('nickname','name','firstsurname','lastsurname','isadmin','job.name','degree.name','link')
#     link = ma.Hyperlinks({"self": ma.URLFor("admin.userCRUD", id="<id>")})

class JobSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Job
        include_fk = True
class PersonSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Person

    link = ma.Hyperlinks(ma.URLFor("admin.userCRUD", id="<id>"))
    name = ma.auto_field()
    firstSurname = ma.auto_field()
    secondSurname = ma.auto_field()
    job = fields.Pluck("self","name")