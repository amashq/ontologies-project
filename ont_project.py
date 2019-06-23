import random
import re
import string

from flask import Flask, render_template

import forms
import api.dbpedia

RU_REGEXP = re.compile(r'[a-яА-Я]+')

app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.SearchForm()
    data = None
    if form.validate_on_submit():
        name_city = form.city.data
        if name_city is None:
            data = []
        else:
            data = api.dbpedia.search_theatres(name_city, api.dbpedia.theatres_city, 'en')
    return render_template('index.html', form=form, data=data)


@app.route('/theatre/<path:uri>', methods=['GET'])
def person(uri):
    profile = api.dbpedia.get_bio(uri)
    persons = api.dbpedia.get_peoples(uri)

    return render_template('theatre.html', profile=profile, persons=persons)