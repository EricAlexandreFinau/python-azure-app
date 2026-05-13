from flask import Flask, Response

app = Flask(__name__)

@app.route("/")
def home():
    return Response("OK AZURE", status=200)
