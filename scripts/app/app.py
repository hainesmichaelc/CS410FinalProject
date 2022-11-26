from flask import Flask
from flask import render_template
from flask import request
#from googlesearch import search
import urllib3
import bs4
import pandas as pd
import json
from datasloth import DataSloth


def create_df_from_json(row, field_name, pk_name, fk_name):
    df = pd.json_normalize(json.loads(row[field_name]))
    if df.size:
        df.insert(0, fk_name, row[pk_name])
    return df


credits = pd.read_csv('./data/tmdb_5000_credits.csv')
movies = pd.read_csv('./data/tmdb_5000_movies.csv')
cast = pd.concat(credits.apply(lambda x: create_df_from_json(
    x, 'cast', 'movie_id', 'movie_id'), axis=1).tolist())
crew = pd.concat(credits.apply(lambda x: create_df_from_json(
    x, 'crew', 'movie_id', 'movie_id'), axis=1).tolist())
genres = pd.concat(movies.apply(
    lambda x: create_df_from_json(x, 'genres', 'id', 'movie_id'), axis=1).tolist())
keywords = pd.concat(movies.apply(
    lambda x: create_df_from_json(x, 'keywords', 'id', 'movie_id'), axis=1).tolist())
production_companies = pd.concat(movies.apply(
    lambda x: create_df_from_json(x, 'production_companies', 'id', 'movie_id'), axis=1).tolist())
spoken_languages = pd.concat(movies.apply(
    lambda x: create_df_from_json(x, 'spoken_languages', 'id', 'movie_id'), axis=1).tolist())
production_countries = pd.concat(movies.apply(
    lambda x: create_df_from_json(x, 'production_countries', 'id', 'movie_id'), axis=1).tolist())
credits = credits.drop(['cast', 'crew'], axis=1)
cast = cast.drop(['cast_id', 'credit_id', 'id'], axis=1)
crew = crew.drop(['credit_id', 'id'], axis=1)
genres = genres.drop(['id'], axis=1)
keywords = keywords.drop(['id'], axis=1)
production_companies = production_companies.drop(['id'], axis=1)
movies = movies.drop(['genres', 'keywords', 'production_companies',
                      'spoken_languages', 'production_countries', 'overview', 'tagline', 'homepage', 'original_title'], axis=1)
sloth = DataSloth()
http = urllib3.PoolManager()
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

"""
@app.route('/googlesearchresult', methods=['POST', 'GET'])
def googlesearchresult():
    if request.method == 'POST':
        # print(request)
        google_search_string = request.form['searchstring']
        search_result = search(google_search_string, num=10, stop=10)
        search_result_string = "<ol type=\"1\">"
        for item in search_result:
            search_result_string += "<li>"
            search_result_string += "<a href=\""
            search_result_string += item
            search_result_string += "\">"
            search_result_string += item
            search_result_string += "</li>"
        # print(google_search_string)
        search_result_string += "</ol>"
        return render_template('googlesearchresult.html', searchstring=google_search_string, searchresult=search_result_string)
"""

@app.route('/imdbbasicsearchresult', methods=['POST', 'GET'])
def imdbbasicesearchresult():
    if request.method == 'POST':
        # print(request)
        imdb_basic_search_string = request.form['searchstring']
        imdb_url = "https://www.imdb.com/find?q=" + \
            imdb_basic_search_string.replace(" ", "+") + "&s=all"

        r = http.request('GET', imdb_url)
        soup = bs4.BeautifulSoup(r.data, 'html.parser')
        # str_imdb_results = soup.findAll('div',{'class':'lister-item-content'})
        # "ipc-metadata-list-summary-item__c"
        str_imdb_results_title = soup.findAll(
            'section', {'data-testid': 'find-results-section-title'})
        if (len(str_imdb_results_title) == 1):
            str_imdb_results_title = str_imdb_results_title[0]
        else:
            str_imdb_results_title = "No IMDb Title Results Found"
        str_imdb_results_name = soup.findAll(
            'section', {'data-testid': 'find-results-section-name'})
        if (len(str_imdb_results_name) == 1):
            str_imdb_results_name = str_imdb_results_name[0]
        else:
            str_imdb_results_name = "No IMDb Name Results Found"

        # str_imdb_results_name = "Name Placeholder"

        str_imdb_results = str_imdb_results_title  # + "<br>" + str_imdb_results_name
        # str_imdb_results = soup.findAll('section',{'data-testid':'find-results-section-title'})[0] + "<br>"
        # str_imdb_results += soup.findAll('section',{'data-testid':'find-results-section-name'})[0]
        # print(str_imdb_results)

        return render_template('imdbbasicsearchresult.html', searchstring=imdb_basic_search_string, imbd_base_results_title=str_imdb_results_title, imbd_base_results_name=str_imdb_results_name)


@app.route('/imdbanswer', methods=['POST', 'GET'])
def imdb_answer():
    if request.method == 'POST':
        question = request.form['searchstring']
        answer = sloth.query(question)
        return render_template('imdbanswer.html', searchstring=question, answer=answer)


app.run(host='0.0.0.0', port=81)
