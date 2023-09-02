from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import os
from find_topics import my_find_topics, my_get_keywords
from app_utils import (
    get_unique_values,
    process_form_entries,
    get_forms,
    get_topic_keywords,
    process_and_flash
)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

try:
    prodURI = os.getenv('DATABASE_URL')
    prodURI = prodURI.replace("postgres://", "postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = prodURI
except Exception:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hansard.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Set TABLE_NAME based on environment variable
TABLE_NAME = 'hansard_2' if 'DYNO' in os.environ else 'hansard'


# Get unique values for year, party, and decade
with db.engine.connect() as connection:
    year_choices = get_unique_values(connection, 'year', TABLE_NAME)
    party_choices = get_unique_values(connection, 'proc_party', TABLE_NAME)
    decade_choices = get_unique_values(connection, 'decade', TABLE_NAME)

# Append 'Any Year' and 'Any Party'
year_choices.append('Any Year')
party_choices.append('Any Party')


class QueryTopics(FlaskForm):
    """
    FlaskForm for querying topics.
    """

    query_string = StringField("Topic Keyword", validators=[DataRequired()])
    submit = SubmitField("Query Topics!")


class GetTopicKeywords(FlaskForm):
    """
    FlaskForm for getting keywords related to a topic.
    """

    topic_id = StringField("Topic ID")
    year = SelectField("Year", choices=year_choices)
    name = StringField("Name")
    party = SelectField("Party", choices=party_choices)
    submit = SubmitField("Get Topic Documents!")


class PickDecadeTopicChart(FlaskForm):
    decade = SelectField("Decade", choices=decade_choices)
    submit = SubmitField("Get Decade Topics!")


# Read graph HTML files
with open('static/top_chart_div.txt', 'r') as openfile:
    graph_html_top = openfile.read()

with open('static/pol_chart_div.txt', 'r', encoding='utf8') as openfile:
    graph_html_pol = openfile.read()


@app.route('/', methods=["GET", "POST"])
def home() -> str:
    """
    Route for the home page.

    Returns:
        str: Rendered HTML template as a string.
    """

    decade_form = PickDecadeTopicChart(decade=2023)

    if decade_form.validate_on_submit():
        d = decade_form.decade.data
        with open(f'static/top_chart_{d}.txt', 'r') as openfile:
            graph_html_dec = openfile.read()

        return render_template("bertopic.html", form=decade_form, graph_html_top=graph_html_top,
                               graph_html_pol=graph_html_pol, graph_html_dec=graph_html_dec)

    with open('static/top_chart_2020.txt', 'r') as openfile:
        graph_html_dec = openfile.read()

    return render_template("bertopic.html", graph_html_top=graph_html_top, form=decade_form,
                           graph_html_pol=graph_html_pol, graph_html_dec=graph_html_dec)


@app.route('/explore', methods=["GET", "POST"])
def explore() -> str:
    """
    Route for the explore page.

    Returns:
        str: Rendered HTML template as a string.
    """

    # Default Values
    DEFAULT_QUERY_STRING = "schools"
    DEFAULT_TOPIC_ID = "0"
    DEFAULT_YEAR = 2023
    DEFAULT_NAME = 'Rishi Sunak'
    DEFAULT_PARTY = 'Conservative'

    query_string = DEFAULT_QUERY_STRING
    topic_id = DEFAULT_TOPIC_ID
    year = DEFAULT_YEAR
    name = DEFAULT_NAME
    party = DEFAULT_PARTY

    query_form, topic_form = get_forms(QueryTopics, GetTopicKeywords, query_string, topic_id, year, name, party)

    if query_form.validate_on_submit() and topic_form.validate_on_submit():
        query_string = query_form.query_string.data
        topics_keyword = my_find_topics(query_string)
        to_show = get_topic_keywords(topics_keyword)

        topic_id = topic_form.topic_id.data
        year = topic_form.year.data
        name = topic_form.name.data
        party = topic_form.party.data

        with db.engine.connect() as connection:
            df_sample = process_form_entries(connection, TABLE_NAME, topic_id, year, name, party)
        topic_example_dict = process_and_flash(df_sample)

        return render_template("explore.html", query_form=query_form,
                               topic_form=topic_form, data_query=to_show,
                               data_dict=topic_example_dict)

    else:
        with db.engine.connect() as connection:
            df_sample = process_form_entries(connection, TABLE_NAME, topic_id, year, name, party)
        topic_example_dict = process_and_flash(df_sample)

        return render_template("explore.html", query_form=query_form,
                               topic_form=topic_form, data_query=[],
                               data_dict=topic_example_dict)


@app.route("/about")
def about() -> str:
    """
    Route for the about page.

    Returns:
        str: Rendered HTML template as a string.
    """

    return render_template("about.html")


if __name__ == "__main__":
    app.run()
