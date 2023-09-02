# app_utils.py

from typing import List, Tuple, Union, Type
from pandas import DataFrame
from sqlalchemy.engine.base import Connection
from flask_wtf import FlaskForm
import pandas as pd
from thefuzz import process
from flask import flash
from find_topics import my_get_keywords


def get_unique_values(connection: Connection, column_name: str, table_name: str) -> List[str]:
    """
    Get the unique values from a specified database column.

    Parameters:
        connection (Connection): The database connection.
        column_name (str): The name of the column to query.
        table_name (str): The name of the table where the column exists.

    Returns:
        List[str]: A list of unique values in the column.
    """
    query = f'SELECT DISTINCT({column_name}) FROM {table_name} ORDER BY {column_name}'
    return list(pd.read_sql(query, connection)[column_name].unique())


def generate_sql_filter(field: str, operator: str, value: str, default_value: Union[str, None] = None) -> str:
    """
    Generate a SQL filter clause string.

    Parameters:
        field (str): The database column name.
        operator (str): SQL operator like 'AND', 'OR', etc.
        value (str): The value to compare against.
        default_value (Union[str, None]): The default value for comparison.

    Returns:
        str: The generated SQL filter clause.
    """

    if value != default_value:
        return f"{operator} {field} = '{value}'"
    return ""


def get_dataframe_from_query(connection: Connection, query: str) -> DataFrame:
    """
    Retrieve a DataFrame from a SQL query.

    Parameters:
        connection (Connection): The database connection.
        query (str): The SQL query string.

    Returns:
        DataFrame: A Pandas DataFrame containing the query results.
    """

    return pd.read_sql(query, connection)


def get_filtered_names(name_query: str, choices: List[str], limit: int = 100, threshold_1: int = 90,
                       threshold_2: int = 70) -> List[str]:
    """
    Get filtered names based on fuzzy string matching.

    Parameters:
        name_query (str): The query string for names.
        choices (List[str]): List of names to match against.
        limit (int): The maximum number of matches to return.
        threshold_1 (int): The primary threshold for fuzzy matching.
        threshold_2 (int): The secondary threshold for fuzzy matching.

    Returns:
        List[str]: A list of filtered names.
    """

    all_results = process.extract(name_query, choices, limit=limit)
    out = [n for n, s in all_results if s >= threshold_1]
    if len(out) == 0:
        out = [n for n, s in all_results if s >= threshold_2]
    return out


def process_form_entries(connection: Connection, table_name: str, topic_id_f: str, year_f: str, name_f: str,
                         party_f: str) -> DataFrame:
    """
    Process the form entries and return a sample DataFrame.

    Parameters:
        connection (Connection): The database connection.
        table_name (str): The name of the database table.
        topic_id_f (str): The topic ID from the form.
        year_f (str): The year from the form.
        name_f (str): The name from the form.
        party_f (str): The party from the form.

    Returns:
        DataFrame: A Pandas DataFrame containing the filtered speeches.
    """
    topic_filter = generate_sql_filter("topic_id", "AND", topic_id_f, "")
    year_filter = generate_sql_filter("year", "AND", year_f, "Any Year")
    party_filter = generate_sql_filter("proc_party", "AND", party_f, "Any Party")
    name_filter = generate_sql_filter("scraped_name", "AND", name_f, "")

    query = f'''SELECT * FROM {table_name} 
                WHERE 1 = 1 
                {topic_filter} 
                {year_filter}
                {party_filter}
                {name_filter}
                LIMIT 100;'''

    df = get_dataframe_from_query(connection, query)
    df_sample = df.sample(5) if len(df) >= 5 else df
    return df_sample


def get_forms(QueryFormClass: Type[FlaskForm], TopicFormClass: Type[FlaskForm], query_string: str, topic_id: str,
              year: str, name: str, party: str) -> Tuple[FlaskForm, FlaskForm]:
    """
    Create and return the query and topic forms.

    Parameters:
        QueryFormClass (Type[FlaskForm]): The class for the query form.
        TopicFormClass (Type[FlaskForm]): The class for the topic keywords form.
        query_string (str): The query string for topics.
        topic_id (str): The topic ID.
        year (str): The year.
        name (str): The name.
        party (str): The party.

    Returns:
        Tuple[FlaskForm, FlaskForm]: A tuple containing the query and topic forms.
    """
    query_form = QueryFormClass(query_string=query_string)
    topic_form = TopicFormClass(
        topic_id=topic_id,
        year=year,
        name=name,
        party=party
    )
    return query_form, topic_form


def get_topic_keywords(topics_keyword: List[int]) -> List[str]:
    """
    Get keywords for a list of topic IDs.

    Parameters:
        topics_keyword (List[int]): List of topic IDs.

    Returns:
        List[str]: A list of topic keywords.
    """

    to_show = []
    for topic_id in topics_keyword[0]:
        text = f"topic #{topic_id} keywords: {my_get_keywords(topic_id)}"
        to_show.append(text)
    return to_show


def process_and_flash(df_sample: DataFrame) -> Union[dict, None]:
    """
    Process the sample DataFrame and flash a message if needed.

    Parameters:
        df_sample (DataFrame): The sample DataFrame.

    Returns:
        Union[dict, None]: A dictionary containing selected columns if the DataFrame is not empty, else None.
    """

    if len(df_sample) == 0:
        flash("No speeches found", 'info')

    return df_sample[['scraped_name', 'proc_party', 'text', 'year', 'person_url', 'topic_id']].to_dict()
