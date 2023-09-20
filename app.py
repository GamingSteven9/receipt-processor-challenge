from flask import Flask, render_template, request, jsonify, json, url_for, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from datetime import date, time
from io import BytesIO
import json
import re
import math
import secrets
import os

UPLOAD_FOLDER = '/app/static/upload_folder'
ALLOWED_EXTENSIONS = {'json'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oursecretkey'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = ['.json']

ids = {}

class receipt(FlaskForm):
    jsonFile = FileField("Insert Receipt", validators=[FileRequired()])
    submit = SubmitField("Generate ID")

class getID(FlaskForm):
    receiptID = StringField("Insert ID")
    submitID = SubmitField("Get Points")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def determinePoints(jDict): # Determines the amount of points from the receipt
    points = 0
    randomid = secrets.token_hex(36)

    for i in jDict:
        match i:

            case 'retailer':
                retailer = re.sub('\W', '', jDict[i]) # Use regex to replace all non-numerical character with an empty string
                points+=len(retailer)
                #print("points: " + str(points))

            case 'purchaseDate':
                pDate = int(date.fromisoformat(jDict[i]).strftime('%d')) #Gets the day from the purchaseDate
                match pDate % 2: #If the date is an odd number add six points
                    case 1:
                        points+=6
                #print("points: " + str(points))

            case 'purchaseTime':
                pTime = time.fromisoformat(jDict[i])
                match pTime > time.fromisoformat('14:00:00') and pTime < time.fromisoformat('16:00:00'): #Check to see if time is between 2 pm and 4 pm
                    case True:
                        points+=10
                #print("points: " + str(points))

            case 'total':
                match float(jDict[i]).is_integer(): #If the total is a round number, add 50 points
                    case True:
                        points+=50
                match float(jDict[i]) % 0.25: #If the total is a multiple of 0.25, add 25 points
                    case 0:
                        points+=25
                #print("points: " + str(points))

            case 'items':
                itemsLength = len(jDict[i])
                match itemsLength % 2:
                    case 0:
                        points+=round((5 * len(jDict[i]) / 2))
                    case 1:
                        points+=round((5 * (len(jDict[i]) - 1) / 2))
                #print("points: " + str(points))

                for j in jDict[i]:
                    match len(j['shortDescription'].strip()) % 3:
                        case 0:
                            points+=math.ceil(float(j['price']) * 0.2) #Use math.ceil(x) to round up
                #print("points: " + str(points))

    #print("points: " + str(points))

    match (randomid in ids):
        case False:
            ids[randomid] = points

    #print(ids)

    return {"id": randomid}

def getPointsFromID(rID): #Gets the points from the given id
    match rID in ids:
            case True:
                return {"points": ids[rID]}

#Render HTML page
@app.route('/',  methods=['GET', 'POST'])
def index():
    return redirect(url_for('receipts')) # Redirect to /receipts

@app.route('/receipts',  methods=['GET', 'POST'])
def receipts():
    jsonFile = False
    Receiptform = receipt()
    receiptID = False
    idForm = getID()

    #url = url_for('')

    #print(Receiptform.submit.data)
    #print(idForm.submitID.data)

    return render_template('index.html', Receiptform=Receiptform, jsonFile=jsonFile, idForm=idForm, receiptID=receiptID)

@app.route('/receipts/process',  methods=['POST'])
def process():
    jsonFile = False
    Receiptform = receipt()
    receiptID = False
    idForm = getID()

    if Receiptform.validate_on_submit():
        jsonData = Receiptform.jsonFile.data
        jsonContent = BytesIO(jsonData.read())
        jsonContent.seek(0)
        content = jsonContent.read() # Turns the json file data into a dictionary
        receiptDict = json.loads(content)
        return jsonify(determinePoints(receiptDict))

    #print(Receiptform.submit.data)
    #print(idForm.submitID.data)

    return render_template('index.html', Receiptform=Receiptform, jsonFile=jsonFile, idForm=idForm, receiptID=receiptID)

@app.route('/receipts/{id}/',  methods=['GET', 'POST'])
def id():
    return redirect(url_for('/receipts/{id}/points')) # Redirect to /receipts

@app.route('/receipts/{id}/points',  methods=['GET', 'POST'])
def points():
    jsonFile = False
    Receiptform = receipt()
    receiptID = False
    idForm = getID()

    if request.method == 'POST':
        receiptID = idForm.receiptID.data
        idForm.receiptID.data = ''
        id = receiptID
        return jsonify(getPointsFromID(receiptID))

    return render_template('index.html', Receiptform=Receiptform, jsonFile=jsonFile, idForm=idForm, receiptID=receiptID)

if __name__ == '__main__':
    app.run(debug=True)