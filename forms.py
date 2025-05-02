from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, DateField, SubmitField
from wtforms.validators import DataRequired

class CreateNewPatientForm(FlaskForm):
  date_time = DateTimeLocalField('Date/Time', validators=[DataRequired()])
  random_mrn = StringField('MRN')
  first_name = StringField('First Name', validators=[DataRequired()])
  last_name = StringField('Last Name', validators=[DataRequired()])
  dob = DateField('D.O.B', validators=[DataRequired()])
  patient_age = StringField('Age', validators=[DataRequired()])
  submit = SubmitField('Create Patient')