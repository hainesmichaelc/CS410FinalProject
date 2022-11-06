from flask import Flask
from flask import render_template
from flask import request
from googlesearch import search
import urllib3
import bs4

http = urllib3.PoolManager()

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/googlesearchresult',methods = ['POST', 'GET'])
def googlesearchresult():
    if request.method == 'POST':
        # print(request)
        google_search_string = request.form['searchstring']
        search_result = search(google_search_string, num=10, stop=10)
        search_result_string = "<ol type=\"1\">"
        for item in search_result:
            search_result_string += "<li>"
            search_result_string += "<a href=\""
            search_result_string +=item
            search_result_string += "\">"
            search_result_string +=item
            search_result_string += "</li>"
        # print(google_search_string)
        search_result_string +="</ol>"
        return render_template('googlesearchresult.html',searchstring=google_search_string, searchresult=search_result_string)

@app.route('/imdbbasicsearchresult',methods = ['POST', 'GET'])
def imdbbasicesearchresult():
     if request.method == 'POST':
        # print(request)
        imdb_basic_search_string = request.form['searchstring']
        imdb_url = "https://www.imdb.com/find?q=" + imdb_basic_search_string.replace(" ","+")

        r = http.request('GET', imdb_url)
        soup = bs4.BeautifulSoup(r.data,'html.parser')
        # str_imdb_results = soup.findAll('div',{'class':'lister-item-content'})
        #"ipc-metadata-list-summary-item__c"
        str_imdb_results_title = soup.findAll('section',{'data-testid':'find-results-section-title'})
        if (len(str_imdb_results_title)==1):
            str_imdb_results_title=str_imdb_results_title[0]
        else:
            str_imdb_results_title="No IMDb Title Results Found"
        str_imdb_results_name = soup.findAll('section',{'data-testid':'find-results-section-name'})
        if (len(str_imdb_results_name)==1):
            str_imdb_results_name=str_imdb_results_name[0]
        else:
            str_imdb_results_name="No IMDb Name Results Found"

        # str_imdb_results_name = "Name Placeholder"

        str_imdb_results = str_imdb_results_title #+ "<br>" + str_imdb_results_name
        # str_imdb_results = soup.findAll('section',{'data-testid':'find-results-section-title'})[0] + "<br>"
        # str_imdb_results += soup.findAll('section',{'data-testid':'find-results-section-name'})[0]
        # print(str_imdb_results)
      
        return render_template('imdbbasicsearchresult.html',searchstring=imdb_basic_search_string, imbd_base_results_title=str_imdb_results_title, imbd_base_results_name=str_imdb_results_name )




app.run(host='0.0.0.0', port=81)
