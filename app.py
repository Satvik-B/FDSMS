from os import name
import firebase_admin
import pyrebase
from firebase_admin import credentials, auth, firestore, storage
import json
from flask import Flask, render_template, url_for, request, redirect , session
from functools import wraps
import datetime
import requests
from requests.exceptions import HTTPError
from flask_session import Session
import os
import tempfile

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD']=True
app.secret_key ='a very very very long string'

cred = credentials.Certificate('fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred,json.load(open('fbConfig.json')))
pyrebase_pb = pyrebase.initialize_app(json.load(open('fbConfig.json')))
db = firestore.client()
bucket = storage.bucket()
# storage = pyrebase_pb.storage()


def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid token provided.'},400
        return f(*args, **kwargs)
    return wrap

@app.route('/api/userinfo')
@check_token
def userinfo():
    return {'data': users}, 200

@app.route('/signup/resturant', methods=['POST', 'GET'])
def restaurantsignup():
    email = request.form['email']
    password = request.form['password']
    area = request.form['area']
    name = request.form['name']
    local_file_path = request.files['local_file_path']
    temp=tempfile.NamedTemporaryFile(delete=False)
    local_file_path.save(temp.name)
    session['sign_message']="Fail"
    
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
    except:
        session['sign_message']="error creating user in firebase"
        return redirect(url_for('restaurantSignup'))
    try:
        json_data = {
            "name" : name,
            "email" : email,
            "area" : area,
            "type" : "Restaurant"
        }
        db.collection("restaurant").document(user.uid).set(json_data)
    except:
        session['sign_message']="error adding user text data in firestore"
        return redirect(url_for('restaurantSignup'))
    try:
        storage_file_path = "restaurantProfilePics/"+user.uid+".jpg"
        blob = bucket.blob(storage_file_path)
        blob.upload_from_filename(temp.name)
        os.remove(temp.name)
        session['sign_message']="Restaurant SignedUp. Please Login"
        return redirect(url_for('login'))
    except:
        session['sign_message']="error uploading photo in firebase storage"
        return redirect(url_for('restaurantSignup'))

@app.route('/signup/deliveryAgent', methods=['POST', 'GET'])
def deliveryAgentsignup():
    email = request.form['email']
    password = request.form['password']
    gender = request.form['gender']
    area = request.form['area']
    mobile = request.form['mobile']
    dob = request.form['dob']
    name = request.form['name']
    local_file_path = request.files['local_file_path']
    temp=tempfile.NamedTemporaryFile(delete=False)
    local_file_path.save(temp.name)
    session['sign_message']="Fail"

    try:
        user = auth.create_user(
            email=email,
            password=password
        )
    except:
        session['sign_message']="error creating user in firebase"
        return redirect(url_for('deliveryAgentSignup'))
    try:
        json_data = {
            "name" : name,
            "dob" : dob,
            "mobile" : mobile,
            "email" : email,
            "gender" : gender,
            "area" : area,
            "type" : "DeliverAgent"
        }
        db.collection("deliveryAgent").document(user.uid).set(json_data)
    except:
        session['sign_message']="error adding user text data in firestore"
        return redirect(url_for('deliveryAgentSignup'))
    try:
        storage_file_path = "deliveryProfilePics/"+user.uid+".jpg"
        blob = bucket.blob(storage_file_path)
        blob.upload_from_filename(temp.name)
        os.remove(temp.name)
        session['sign_message']="Delivery Agent SignedUp. Please Login"
        return redirect(url_for('login'))
    except:
        session['sign_message']="error uploading photo in firebase storage"
        return redirect(url_for('deliveryAgentSignup'))



@app.route('/signup/api', methods=['POST','GET'])
def signup():

    email = request.form['email']
    password = request.form['password']
    gender = request.form['gender']
    area = request.form['area']
    mobile = request.form['mobile']
    dob = request.form['dob']
    name = request.form['name']
    local_file_path = request.files['local_file_path']
    temp=tempfile.NamedTemporaryFile(delete=False)
    local_file_path.save(temp.name)

    try:
        user = auth.create_user(
            email=email,
            password=password
        )
    except:
        session['sign_message']="error creating user in firebase"
        return redirect(url_for('customerSignup'))
    try:
        json_data = {
            "name" : name,
            "dob" : dob,
            "mobile" : mobile,
            "email" : email,
            "gender" : gender,
            "area" : area,
            "type" : "Customer"
        }
        db.collection("customers").document(user.uid).set(json_data)
    except:
        session['sign_message']="error adding user text data in firestore"
        return redirect(url_for('customerSignup'))
    try:
        storage_file_path = "customerProfilePics/"+user.uid+".jpg"
        blob = bucket.blob(storage_file_path)
        blob.upload_from_filename(temp.name)
        session['sign_message']="Customer Signed Up. Please Login."
        return redirect(url_for('login'))
    except:
        session['sign_message']="error uploading photo in firebase storage"
        return redirect(url_for('customerSignup'))

@app.route("/temp")
def temp():
    blob = bucket.blob("customerProfilePics/"+"YQ2pF5uHW7ZCvfpIzUD1sTcZL5n2"+".jpg")

    str = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    print(str)
    return str,200

@app.route('/api/token')
def token():
    email = request.form.get('email')
    password = request.form.get('password')
    # email="aryanag65@gmail.com"
    # password="88080ary"
    try:
        user = pyrebase_pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']

        # user = pyrebase_pb.auth().get_account_info(jwt)
        # print(user)

        session['token_jwt']=jwt
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error logging in'},400

@app.route('/')
def index():
    session['sign_message']="False"
    message=session['sign_message']
    return render_template('index.html', message=message)

@app.route('/Signup')
def signUp():
    return render_template('signup.html')



@app.route('/login')
def login():
    message=session['sign_message']
    return render_template('login.html', message=message)

@app.route('/adminLogin')
def adminLogin():
    return render_template('adminLogin.html')

@app.route('/customerSignup')
def customerSignup():
    message=session['sign_message']
    return render_template('customerSignup.html', message=message)

@app.route('/restaurantSignup')
def restaurantSignup():
    message=session['sign_message']
    return render_template('restaurantSignup.html', message=message)

@app.route('/deliveryAgentSignup')
def deliveryAgentSignup():
    message=session['sign_message']
    return render_template('deliveryAgentSignup.html', message=message)

if __name__ == "__main__":
    # cache.init_app(app)
    app.run(debug=True)