from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    city = StringField('city', validators=[DataRequired()])
    api = RadioField('API', choices=[('dbpedia', 'DBPedia'), ('wikidata', 'WikiData')], default='dbpedia')
    submit = SubmitField('Search')
