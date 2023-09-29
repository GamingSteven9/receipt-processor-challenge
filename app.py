from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError
from datetime import date, time
from io import BytesIO
from json import loads
from re import sub
from math import ceil
from secrets import token_hex
from os import path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oursecretkey'

ids = {} # Dictionary used to store the ids, where the ID is the key and the points are the value

# The form that handles the JSON receipt
class receipt(FlaskForm):
    jsonFile = FileField("Insert Receipt", validators=[FileRequired()]) # Requires a file for 'submitFile' to go through
    submitFile = SubmitField("Generate ID")

    def validateFile(self, name): # Check if the given file is a JSON file
        
        match (path.splitext(name))[-1]: # If the input file is not a JSON file, then raise an error
            case '.json':
                pass
            case _:
                raise ValidationError("The file must be a json file")

# The form that handles the ID            
class getID(FlaskForm):
    receiptID = StringField("Insert ID", validators=[DataRequired()]) # Requires an input in the StringField for 'submitID' to go through
    submitID = SubmitField("Get Points")

# Determines the amount of points from the receipt
def determinePoints(jDict):
    points = 0 # Holds the current amount of points that the receipt currently has

    for i in jDict: # Matches each item in the receipt
        match i:

            case 'retailer':
                retailer = sub('\W', '', jDict[i]) # Use regex to replace all non-alphanumerical character with an empty string, then add 1 point for each alphanumerical character
                points+=len(retailer)

            case 'purchaseDate':
                pDate = int(date.fromisoformat(jDict[i]).strftime('%d')) # The day of purchase
                match pDate % 2: # If the day is an odd number then add 6 points
                    case 1:
                        points+=6
                    case _:
                        pass

            case 'purchaseTime':
                pTime = time.fromisoformat(jDict[i]) # The purchase time
                match pTime > time.fromisoformat('14:00:00') and pTime < time.fromisoformat('16:00:00'): # If time is between 2 pm and 4 pm, then add 10 points
                    case True:
                        points+=10
                    case _:
                        pass

            case 'total':
                match float(jDict[i]).is_integer(): # If the total is a round number, then add 50 points
                    case True:
                        points+=50
                    case _:
                        pass

                match float(jDict[i]) % 0.25: # If the total is a multiple of 0.25, then add 25 points
                    case 0:
                        points+=25
                    case _:
                        pass

            case 'items':
                itemsLength = len(jDict[i])
                match itemsLength % 2: # Determine if the number of items in the receipt is a multiple of 2
                    case 0:
                        points+=round((5 * len(jDict[i]) / 2)) # If the number of the items is even, then divide the length by 2 to get the number of pairs and then multiply the remainder by 5 to get the points
                    case 1:
                        points+=round((5 * (len(jDict[i]) - 1) / 2)) # If the number of the items is odd, subtract one from it to make it a multiple of 2, then divide the number by 2 to get the number of pairs, 
                                                                        # and then multiply the remainder by 5 to get the number of points earned.
                    case _:
                        pass

                for j in jDict[i]:
                    match len(j['shortDescription'].strip()) % 3: # If the trimmed length of an item's description is a multiple of 3, multiply the price by 0.2 and round it up to the nearest integer using ceil(x) 
                                                                    # to get the number of points earned.
                        case 0:
                            points+=ceil(float(j['price']) * 0.2)
                        case _:
                            pass
            
            case _:
                pass

    return points # Return the total amount of points

def addID(points): # Assign the points to an ID and add it to 'ids'
    randomid = token_hex(4) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(6) # Generate a random ID

    match (randomid in ids): # If the ID is not already present in 'ids,' assign the points to it. Otherwise, create a new ID until the new one is not in 'ids'
        case False:
            ids[randomid] = points # Assign the points to an ID
        case True:
            while randomid in ids:
                randomid = token_hex(4) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(6) # Generate a new random ID
        case _:
            pass
        
    return {"id": randomid}

def getPointsFromID(rID): # Gets the points from the given ID
    match rID in ids:
            case True:
                return {"points": ids[rID]}
            case _:
                pass

# Redirect to /receipts
@app.route('/',  methods=['GET', 'POST'])
def index():
    return redirect(url_for('receipts'))

# Render the home page
@app.route('/receipts',  methods=['GET', 'POST'])
def receipts():

    # Initialize instances of the classes along with their properties
    jsonFile = False
    receiptID = False
    ReceiptForm = receipt()
    IDForm = getID()

    match ReceiptForm.submitFile.data: # Operates on the data from the ReceiptForm
        case True:
            jsonData = ReceiptForm.jsonFile.data 
            ReceiptForm.validateFile(request.files['jsonFile'].filename) # Check if the given file is a JSON file
            jsonContent = BytesIO(jsonData.read())
            jsonContent.seek(0)
            session["dictID"] = loads(jsonContent.read())
            jsonContent.close()
            return redirect(url_for('process'), code=307) # Redirect to /receipts/process using code 307 to repeat the POST request from the 'submitFile' button
        case _:
            pass
    
    match IDForm.submitID.data: # Operates on the data from the idForm
        case True:
            receiptID = IDForm.receiptID.data
            session["sessionID"] = receiptID
            pointsURL = url_for('points', id=receiptID) # Get the url for /receipts/<id>/points with the given ID
            return redirect(pointsURL) # Redirect to /receipts/<id>/points
        case _:
            pass

    return render_template('index.html', ReceiptForm=ReceiptForm, IDForm=IDForm, jsonFile=jsonFile, receiptID=receiptID) 

@app.route('/receipts/process',  methods=['POST']) # A post endpoint that takes a JSON receipt and returns a JSON object with a randomly generated ID
def process():
    return jsonify(addID(determinePoints(session["dictID"])))

@app.route('/receipts/<id>/points',  methods=['GET']) # A getter endpoint that looks up the receipt by the ID and returns a JSON object with the number of points awarded
def points(id):
    return jsonify(getPointsFromID(session["sessionID"]))

if __name__ == '__main__':
    app.run(debug=True)