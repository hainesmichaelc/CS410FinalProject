from flask import Flask
from flask import render_template
from flask import request
from googlesearch import search
import urllib3
import bs4
import pandas as pd
import json
from datasloth import DataSloth
from imdb import Cinemagoer
import time

ia = Cinemagoer()


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
# sloth = DataSloth()
sloth = DataSloth(openai_api_key="sk-vKvOuoFAKE_FAKE_FAKE_FAKE_fZmmYDlUcif2f") # put your key here this is fake

http = urllib3.PoolManager()
app = Flask(__name__)

def getGoogleResult(google_search_string):
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
        return search_result_string

def getBasicIMDBResult(imdb_basic_search_string):
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

        # movies = ia.search_movie('imdb_basic_search_string')
        # names = ia.search_person('imdb_basic_search_string')


        # print(movies)
        # print(names)

        # str_imdb_results_name = "Name Placeholder"

        #str_imdb_results = str_imdb_results_title  + "<br>" + str_imdb_results_name   
        return str_imdb_results_title, str_imdb_results_name

def getIMDBResultsName(searchString):
    
    people = ia.search_person(searchString)
    str_imdb_results_name="<ol type=\"1\">"
    for person in people:
        curUrl =ia.get_imdbURL(person)
        str_imdb_results_name +="<li>"
        cur_html="<a href=\"" + curUrl + "\"> " + person['name'] 
        str_imdb_results_name+=cur_html
        str_imdb_results_name+="</li>"
    str_imdb_results_name += "</ol>" 

    return str_imdb_results_name

def getIMDBResultsTitle(searchString):
    
    movies = ia.search_movie(searchString)
    str_imdb_results_title="<ol type=\"1\">"
    for item in movies:
        curUrl =ia.get_imdbURL(item)
        str_imdb_results_title +="<li>"
        cur_html="<a href=\"" + curUrl + "\"> " + item['title'] 
        str_imdb_results_title+=cur_html
        str_imdb_results_title+="</li>"
    str_imdb_results_title += "</ol>" 


    return str_imdb_results_title

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/googlesearchresult', methods=['POST', 'GET'])
def googlesearchresult():
    if request.method == 'POST':
        # print(request)
        google_search_string = request.form['searchstring']
        search_result_string = getGoogleResult(google_search_string)

        return render_template('googlesearchresult.html', searchstring=google_search_string, searchresult=search_result_string)

@app.route('/imdbbasicsearchresult', methods=['POST', 'GET'])
def imdbbasicesearchresult():
    if request.method == 'POST':
        # print(request)
        imdb_basic_search_string = request.form['searchstring']
        
        str_imdb_results_title=getIMDBResultsTitle(imdb_basic_search_string)
        if (len(str_imdb_results_title)==18):
            time.sleep(3)
            str_imdb_results_title = getIMDBResultsTitle(imdb_basic_search_string)
        str_imdb_results_name=getIMDBResultsName(imdb_basic_search_string)
        if (len(str_imdb_results_name)==18):
            time.sleep(3)
            str_imdb_results_name=getIMDBResultsName(imdb_basic_search_string)

        # str_imdb_results_title,str_imdb_results_name=getBasicIMDBResult(imdb_basic_search_string)
        
        # str_imdb_results = soup.findAll('section',{'data-testid':'find-results-section-title'})[0] + "<br>"
        # str_imdb_results += soup.findAll('section',{'data-testid':'find-results-section-name'})[0]
        # print(str_imdb_results)

        return render_template('imdbbasicsearchresult.html', \
            searchstring=imdb_basic_search_string, \
            imbd_base_results_title=str_imdb_results_title, \
            imbd_base_results_name=str_imdb_results_name)


@app.route('/imdbanswer', methods=['POST', 'GET'])
def imdb_answer():
    if request.method == 'POST':
        question = request.form['searchstring']
        answer = sloth.query(question)
        return render_template('imdbanswer.html', searchstring=question, answer=answer)

@app.route('/combinedsearchresult', methods=['POST', 'GET'])
def combined_search_result():
    if request.method == 'POST':
        question = request.form['searchstring']

        google_result_string = getGoogleResult(question)

        # str_imdb_results_title,str_imdb_results_name=getBasicIMDBResult(question)
        str_imdb_results_title=getIMDBResultsTitle(question)
        if (len(str_imdb_results_title)==18):
            time.sleep(3)
            str_imdb_results_title = getIMDBResultsTitle(question)
        str_imdb_results_name=getIMDBResultsName(question)
        if (len(str_imdb_results_name)==18):
            time.sleep(3)
            str_imdb_results_name=getIMDBResultsName(question)

        answer = sloth.query(question)
        return render_template('combinedsearchresult.html', 
            searchstring=question, \
            googlesearchresult=google_result_string, \
            basicimdbsearchtitle = str_imdb_results_title, \
            basicimdbsearchname = str_imdb_results_name, \
            teammksearchresult=answer)

app.run(host='0.0.0.0', port=81)
