""" Application forms in the main blueprint. """

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Form class definition
class NameForm(FlaskForm):
    name = StringField('What is you name?', validators=[DataRequired()])
    submit = SubmitField('Submit')