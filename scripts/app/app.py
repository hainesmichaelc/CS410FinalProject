from flask import Flask
from flask import render_template
from flask import request
from googlesearch import search

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
        search_result_string = ""
        for item in search_result:
            search_result_string += "<div>"
            search_result_string +=item
            search_result_string += "</div>"
            search_result_string +="<br>"
        # print(google_search_string)
        return render_template('googlesearchresult.html',searchstring=google_search_string, searchresult=search_result_string)


app.run(host='0.0.0.0', port=81)
