from .models import *
from database import db
from wtforms_alchemy import model_form_factory, QuerySelectField
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,BooleanField,FileField,PasswordField, TextAreaField, MultipleFileField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField as qs
from wtforms.validators import DataRequired, Length

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class codeForm(ModelForm):
    class Meta:
        model = Code
        exclude = ['available']


class branchForm(ModelForm):
    class Meta:
        model = Branch
        exclude = ['active']


class projectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ['active', 'journals']
    person_id = QuerySelectField(
        query_factory=lambda: Person.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: "{0} {1}, {2}".format(a.firstSurname, a.secondSurname, a.name),
        allow_blank=False,
        label='User Name',
    )
    branch_id = QuerySelectField(
        query_factory=lambda: Branch.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='Branch Name',
    )

class consecutiveForm(ModelForm):
    class Meta:
        model = Consecutive

    table_name_id = QuerySelectField(
        query_factory=lambda: TableRef.query.filter_by(isHidden=0).order_by(text("description asc")),
        get_pk=lambda a: a.name,
        get_label=lambda a: a.description,
        allow_blank=False,
        label='Table Name',
    )
    type_id = QuerySelectField(
        query_factory=lambda: Code.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.description,
        allow_blank=False,
        label='Code'
    )


class jobForm(ModelForm):
    class Meta:
        model = Job
        exclude = ['active']
    user_role_id = QuerySelectField(
        query_factory=lambda: UserRole.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='User Role'
    )


class userRoleForm(ModelForm):
    class Meta:
        model = UserRole
        exclude = ['active']


class degreeForm(ModelForm):
    class Meta:
        model = Degree
        exclude = ['active']


class personForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password')
    isAdmin = BooleanField('Give admin rigths')
    name = StringField('First Name', validators=[DataRequired()])
    firstSurname = StringField('First Surname', validators=[DataRequired()])
    secondSurname = StringField('Second Surname', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    degree_id = qs(
        query_factory=lambda: Degree.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='Academic Degree'
    )
    job_id = qs(
        query_factory=lambda: Job.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='Job/Role'
    )
    signature = FileField('Signature')
    photo = FileField('Photography')

class equipmentForm(ModelForm):
    class Meta:
        model = Equipment
        exclude = ['active']


class experimentForm(ModelForm):
    class Meta:
        model = Experiment
        exclude = ['active']
    photos = MultipleFileField('Experiment Photos')
    main_objective = TextAreaField(u'Main Objective', validators=[DataRequired(), Length(max=3000)])
    project_id = qs(
        query_factory=lambda: Project.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name,
        allow_blank=False,
        label='Project Name'
    )
    experimenter_id = QuerySelectField(
        query_factory=lambda: Person.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: "{0} {1}, {2}".format(a.firstSurname, a.secondSurname, a.name),
        allow_blank=False,
        label='Experimenter Name',
    )

    witness_id = QuerySelectField(
        query_factory=lambda: Person.getByAll(),
        get_pk=lambda a: a.id,
        get_label=lambda a: "{0} {1}, {2}".format(a.firstSurname, a.secondSurname, a.name),
        allow_blank=False,
        label='Assistant Name',
    )


class LoginForm(FlaskForm):
    nickname = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')