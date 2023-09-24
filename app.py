from flask import Flask, render_template, request, jsonify, json, url_for, redirect, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError
from datetime import date, time
from io import BytesIO
import json
import re
import math
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oursecretkey' # Intialize the secret key

ids = {}

class receipt(FlaskForm): # The form that handles the json file
    jsonFile = FileField("Insert Receipt", validators=[FileRequired()]) # Requires a file for the submit button to go through
    submit = SubmitField("Generate ID")

    def validateFile(self, name):
        
        match (os.path.splitext(name))[-1]: # If the input file is not a json file, raise an error
            case '.json':
                pass
            case _:
                raise ValidationError("The file must be a json file")
            
class getID(FlaskForm): # The form that handles the id
    receiptID = StringField("Insert ID", validators=[DataRequired()]) # Requires an input for the submit button to go through
    submitID = SubmitField("Get Points")

def determinePoints(jDict): # Determines the amount of points from the receipt
    points = 0 # Variable thats holds the total amount of points

    for i in jDict: # Matches each item in the receipt
        match i:

            case 'retailer':
                retailer = re.sub('\W', '', jDict[i]) # Use regex to replace all non-numerical character with an empty string
                points+=len(retailer)

            case 'purchaseDate':
                pDate = int(date.fromisoformat(jDict[i]).strftime('%d')) #Gets the day from the purchaseDate
                match pDate % 2: #If the date is an odd number then add six points
                    case 1:
                        points+=6

            case 'purchaseTime':
                pTime = time.fromisoformat(jDict[i])
                match pTime > time.fromisoformat('14:00:00') and pTime < time.fromisoformat('16:00:00'): # If time is between 2 pm and 4 pm add 10 points
                    case True:
                        points+=10

            case 'total':
                match float(jDict[i]).is_integer(): # If the total is a round number, add 50 points
                    case True:
                        points+=50
                match float(jDict[i]) % 0.25: # If the total is a multiple of 0.25, add 25 points
                    case 0:
                        points+=25

            case 'items':
                itemsLength = len(jDict[i])
                match itemsLength % 2: # Determine if the number of items in the receipt is a multiple of 2
                    case 0:
                        points+=round((5 * len(jDict[i]) / 2)) # If the length of the items are even then we divide the length by 2 to get the number of pairs and then multiple the "reaminder" by 5 to get the points
                    case 1:
                        points+=round((5 * (len(jDict[i]) - 1) / 2)) # If the length of the items are odd, we first subtract it by one to make it a multiple of 2, then we divide the length by 2 to get the number of pairs and then multiple the "reaminder" by 5 to get the points
                    case _:
                        pass

                for j in jDict[i]:
                    match len(j['shortDescription'].strip()) % 3: # Determine if the trimmed length of an item's description is a multiple of 3
                        case 0:
                            points+=math.ceil(float(j['price']) * 0.2) # Use math.ceil(x) to round up the points from the description
                        case _:
                            pass
            
            case _:
                pass

    return points

def addID(points): # Attaches the points to an id and add it to the dictionary
    randomid = secrets.token_hex(4) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(6) # Generate a random id

    match (randomid in ids): # If the id is not int already present in ids, attach it to the points
        case False:
            ids[randomid] = points
        case True:
            while randomid in ids:
                randomid = secrets.token_hex(4) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(6) # Generate a new random id
        case _:
            pass
        
    return {"id": randomid}

def getPointsFromID(rID): # Gets the points from the given id
    match rID in ids:
            case True:
                return {"points": ids[rID]}
            case _:
                pass

@app.route('/',  methods=['GET', 'POST'])
def index():
    return redirect(url_for('receipts')) # Redirect to /receipts

#Render the home page
@app.route('/receipts',  methods=['GET', 'POST'])
def receipts():
    jsonFile = False
    receiptID = False
    Receiptform = receipt()
    idForm = getID()

    match Receiptform.submit.data: # Operates on the data from the Receiptform
        case True:
            jsonData = Receiptform.jsonFile.data
            Receiptform.validateFile(request.files['jsonFile'].filename)
            jsonContent = BytesIO(jsonData.read())
            jsonContent.seek(0)
            content = jsonContent.read() # Turns the json file data into a dictionary
            session["dictID"] = json.loads(content)
            jsonContent.close()
            return redirect(url_for('process'), code=307) # Redirect with a code of 307 to make it method's post (Comeback)
        case _:
            pass
    
    match idForm.submitID.data: # Operates on the data from the idForm
        case True:
            receiptID = idForm.receiptID.data
            session["sessionID"] = receiptID
            pointsURL = url_for('points', id=receiptID)
            return redirect(pointsURL) # Redirect to /receipts
        case _:
            pass

    return render_template('index.html', Receiptform=Receiptform, jsonFile=jsonFile, idForm=idForm, receiptID=receiptID) 

@app.route('/receipts/process',  methods=['POST'])
def process():
    return jsonify(addID(determinePoints(session["dictID"])))

@app.route('/receipts/<id>/points',  methods=['GET'])
def points(id):
    return jsonify(getPointsFromID(session["sessionID"]))

if __name__ == '__main__':
    app.run(debug=True)