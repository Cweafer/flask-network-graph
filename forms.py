from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.form import Form

class SearchForm(Form):
  submission_id = StringField('search', [DataRequired()])
