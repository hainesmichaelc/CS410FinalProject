from flask import Flask
from flask import render_template
from flask import request
from googlesearch import search
import urllib3
import bs4
import pandas as pd
import sqlite3
from datasloth import DataSloth
from imdb import Cinemagoer
import time
import config as cfg

ia = Cinemagoer()

# connect to the SQLite database and read the data into memory
conn = sqlite3.connect('./db/movies.db')
movies = pd.read_sql_query("select * from movies", conn)
production_companies = pd.read_sql_query(
    "select * from production_companies", conn)
cast = pd.read_sql_query("select * from cast", conn)
crew = pd.read_sql_query("select * from crew", conn)
genres = pd.read_sql_query("select * from genres", conn)
keywords = pd.read_sql_query("select * from keywords", conn)

# initialize the OpenAI API connection, request pool manager, and Flask app
sloth = DataSloth(openai_api_key=cfg.openai_api_key)
http = urllib3.PoolManager()
app = Flask(__name__)


# search google via HTTP request
def google_search(search_string):
    search_result = search(search_string, num=10, stop=10)
    result = "<ol type=\"1\">"
    for item in search_result:
        result += "<li><a href=\"" + item + "\">" + item + "</a></li>"
    result += "</ol>"
    return result


# search imdb people via HTTP request
def imdb_search(search_string):
    url = "https://www.imdb.com/find?q=" + \
        search_string.replace(" ", "+") + "&s=all"
    headers = { 'User-Agent': cfg.browser }
    req = http.request('GET', url, headers=headers)
    soup = bs4.BeautifulSoup(req.data, 'html.parser')
    res_title = soup.findAll(
        'section', {'data-testid': 'find-results-section-title'})
    if (len(res_title) == 1):
        res_title = res_title[0]
    else:
        res_title = "None found"
    res_name = soup.findAll(
        'section', {'data-testid': 'find-results-section-name'})
    if (len(res_name) == 1):
        res_name = res_name[0]
    else:
        res_name = "None found"
    return res_title, res_name


# search imdb people via HTTP request
def imdb_search_people(search_string):
    people = ia.search_person(search_string)
    results = "<ol>"
    for person in people:
        url = ia.get_imdbURL(person)
        results += "<li><a href=\"" + url + "\">" + person['name'] + "</a></li>"
    results += "</ol>"
    return results


# search imdb movies via HTTP request
def imdb_search_movies(search_string):
    movies = ia.search_movie(search_string)
    results = "<ol>"
    for movie in movies:
        url = ia.get_imdbURL(movie)
        results += "<li><a href=\"" + url + "\">" + movie['title'] + "</a></li>"
    results += "</ol>"
    return results


# format GPT-3 answer 
def format_answer(answer):
    if answer is None or answer.shape[0] == 0:
        return "D'oh! We couldn't answer that one..."
    elif answer.shape == (1, 1):
        return answer.iloc[0][0]
    elif answer.shape[0] > 100:
        return " Limiting to first 100 results...<br /><br />" + answer[0:100].to_html()
    else:
        return "<br /><br />" + answer.to_html()


# home page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# execute all searches
@app.route('/result', methods=['POST', 'GET'])
def search_result():
    if request.method == 'POST':
        question = request.form['searchstring']
        if question:
            answer = sloth.query(question, {
                "m": movies, "ca": cast, "cr": crew, "p": production_companies, "g": genres, "k": keywords})
            db_query = sloth.last_prompt[1].replace("\n", "<br />")
            google_results = google_search(question)
            imdb_movies, imdb_people = imdb_search(question)
            return render_template('result.html',
                                search_string=question,
                                answer=format_answer(answer),
                                db_query=db_query,
                                imdb_movies=imdb_movies,
                                imdb_people=imdb_people,
                                google_results=google_results)
        return render_template('notfound.html')

app.run(host='0.0.0.0', port=81)
