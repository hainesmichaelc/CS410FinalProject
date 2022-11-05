from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


# @app.route('/')
# def index():
#     return 'Web App with Python Flask!'

@app.route('/')
@app.route('/index')
def index():
    name = 'Rosalia'
    return render_template('index.html')

@app.route('/googlesearchresult',methods = ['POST', 'GET'])
def googlesearchresult():
    if request.method == 'POST':
        # print(request)
        google_search_string = request.form['searchstring']
        # print(google_search_string)
        return render_template('googlesearchresult.html',searchstring=google_search_string)


app.run(host='0.0.0.0', port=81)
