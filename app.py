from flask import Flask
from flask import render_template
from flask import request
from googlesearch import search
import urllib3
import bs4
import pandas as pd
import sqlite3
from datasloth import DataSloth
import time
import config as cfg


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
def imdb_search_movies(search_string):
    url = "https://www.imdb.com/find?q=" + \
        search_string.replace(" ", "+") + "&s=all"
    headers = {'User-Agent': cfg.browser}
    req = http.request('GET', url, headers=headers)
    soup = bs4.BeautifulSoup(req.data, 'html.parser')
    res_title = soup.findAll(
        'section', {'data-testid': 'find-results-section-title'})
    if (len(res_title) == 1):
        list_titles = res_title[0].contents[1].contents[0].contents
        if isinstance(list_titles[0], str):
            return list_titles[0]
        titles = [title.contents[1].contents[0].contents[0].contents[0] for title in list_titles]
        links = [title.contents[1].contents[0].contents[0].attrs["href"] for title in list_titles]
        titles_html = "<ol>"
        for i in range(0, len(titles)):
            titles_html += "<li><a href=\"https://www.imdb.com" + links[i] + \
            "\">" + titles[i] + "</a></li>"
        titles_html += "</ol>"
        return titles_html
    return "No results found..."


# search imdb movies via HTTP request
def imdb_search_people(search_string):
    url = "https://www.imdb.com/find?q=" + \
        search_string.replace(" ", "+") + "&s=all"
    headers = {'User-Agent': cfg.browser}
    req = http.request('GET', url, headers=headers)
    soup = bs4.BeautifulSoup(req.data, 'html.parser')
    res_name = soup.findAll(
        'section', {'data-testid': 'find-results-section-name'})
    if (len(res_name) == 1):
        list_names = res_name[0].contents[1].contents[0].contents
        if isinstance(list_names[0], str):
            return list_names[0]
        names = [name.contents[1].contents[0].contents[0].contents[0] for name in list_names]
        links = [name.contents[1].contents[0].contents[0].attrs["href"] for name in list_names]
        names_html = "<ol>"
        for i in range(0, len(names)):
            names_html += "<li><a href=\"https://www.imdb.com" + links[i] + \
            "\">" + names[i] + "</a></li>"
        names_html += "</ol>"
        return names_html
    return "No results found..."


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
            imdb_movies = imdb_search_movies(question)
            imdb_people = imdb_search_people(question)
            return render_template('result.html',
                                   search_string=question,
                                   answer=format_answer(answer),
                                   db_query=db_query,
                                   imdb_movies=imdb_movies,
                                   imdb_people=imdb_people,
                                   google_results=google_results)
        return render_template('notfound.html')


app.run(host='0.0.0.0', port=81)
