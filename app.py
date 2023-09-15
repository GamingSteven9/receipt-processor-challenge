from flask import Flask, render_template, request
app = Flask(__name__)

#Render HTML page
@app.route('/', methods=['POST', "GET"])
def index():
    return render_template('index.html')