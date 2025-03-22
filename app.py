import mysql.connector
from flask import Flask, render_template, request, redirect
from flask_restful import Api,Resource
import hashlib,base64
import validators.url

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="MyAdmin",
    database="URLSHORTNER"
)

cursor = conn.cursor()

def exists_url(url):
    query = f"SELECT * FROM urls WHERE original_link = '{url}'"
    cursor.execute(query)

    exists = cursor.fetchone()
    if exists:
        return exists
    else:
        return False

def add_url(original_link,shorten_link):
    cursor.execute("INSERT INTO urls (original_link, shorten_link) VALUES (%s, %s)",(original_link,shorten_link))
    conn.commit()

def url_shortner(full_url):
    full_url = full_url
    hash = hashlib.sha256(full_url.encode())
    url = base64.urlsafe_b64encode(hash.digest()).decode()[:7]
    return url

def get_original_url(shorten_link):
    cursor.execute("SELECT * FROM urls WHERE shorten_link = %s", (shorten_link,))
    return cursor.fetchone()[0]

app = Flask(__name__)
MyApi = Api(app)

class UrlShortener(Resource):
    def get(self,link):
        return redirect(get_original_url(link))

MyApi.add_resource(UrlShortener, "/<string:link>")
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/url",methods=["POST"])
def url():
    if request.method == "POST":
        full_url = request.form["url_field"]
        if not (full_url.startswith("http://") or full_url.startswith("https://")):
            full_url = "http://" + full_url.replace("www","")
        else:
            full_url = "http://" + full_url.replace("www", "")
        if validators.url(full_url):
            existsUrl = exists_url(full_url)
            if existsUrl != False:
                return render_template("url.html",short_url=existsUrl[1])
            else:
                short_url = url_shortner(full_url)
                add_url(full_url,short_url)
                return render_template("url.html",short_url=short_url)
        else:
            return "Invalid URL"
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")