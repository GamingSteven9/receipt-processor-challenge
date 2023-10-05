from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError
from process import determinePoints, createRandomID, addID
from points import getPointsFromID
from io import BytesIO
from json import loads
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
            session["givenReceipt"] = loads(jsonContent.read())
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

@app.route('/receipts/process', methods=['POST']) # A post endpoint that takes a JSON receipt and returns a JSON object with a randomly generated ID
def process():
    points = (determinePoints(session["givenReceipt"])) # Stores the points from the given receipt for later use
    id = createRandomID(ids) # Stores the random id in a variable for later use
    addID(ids, id, points) # Adds the given {"id", points} pair to ids
    print(ids)
    return jsonify({"id": id})

@app.route('/receipts/<id>/points', methods=['GET']) # A getter endpoint that looks up the receipt by the ID and returns a JSON object with the number of points awarded
def points(id):
    idPoints = getPointsFromID(session["sessionID"], ids) # Stores the points from the given "id"
    return jsonify( {"points": idPoints})

if __name__ == '__main__':
    app.run(debug=True)