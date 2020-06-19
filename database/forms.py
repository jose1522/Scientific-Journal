from .models import *
from wtforms_alchemy import ModelFormField, model_form_factory, QuerySelectField
from flask_wtf import FlaskForm
from database.database import db
BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class consecutiveForm(ModelForm):
    class Meta:
        model = Consecutive

    table_name_id = QuerySelectField(
        query_factory=lambda: TableRef.query.filter_by(isHidden=0).order_by(text("description asc")),
        get_pk=lambda a: a.name,
        get_label=lambda a: a.description,
        allow_blank=False,
        label='Table Name'
    )
    type_id = QuerySelectField(
        query_factory=lambda: Code.query.order_by(text("description asc")),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.description,
        allow_blank=False,
        label='Code'
    )

class jobForm(ModelForm):
    class Meta:
        model = Job
    user_role_id = QuerySelectField(
        query_factory=lambda: UserRole.query.filter_by(active=1).order_by(text("name asc")),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='Code'
    )
