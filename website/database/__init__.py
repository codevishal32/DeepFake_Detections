import firebase_admin
from firebase_admin import credentials
from pyrebase import initialize_app

# Initialize Firebase using firebase_admin
cred = credentials.Certificate("database/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://first-flask-app-37729-default-rtdb.firebaseio.com/",
    "storageBucket": "first-flask-app-37729.appspot.com"
})

# Initialize Firebase using pyrebase
firebaseConfig = {
    'apiKey': "AIzaSyDbzwOJ3wC4SXYORzjYOTHhD6xoF5azHCo",
    'authDomain': "first-flask-app-37729.firebaseapp.com",
    'databaseURL': "https://first-flask-app-37729-default-rtdb.firebaseio.com",
    'projectId': "first-flask-app-37729",
    'storageBucket': "first-flask-app-37729.appspot.com",
    'messagingSenderId': "971195377037",
    'appId': "1:971195377037:web:d55d9c67f47386477409c4",
    'measurementId': "G-7JVJTC70JR"
}

auth = initialize_app(firebaseConfig).auth()