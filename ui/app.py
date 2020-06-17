from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es  = Elasticsearch()

@app.route('/')
def index():
    return render_template('index.html',response='')

@app.route('/search',methods=["POST"])
def search():
    if(request.method == "POST"):
        resp = es.search(index='sinhalalyrics')
        query = request.form['query']
    return render_template('index.html',response=resp)
 
if __name__ == '__main__':
    app.DEBUG = True
    app.run()