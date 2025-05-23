import pyrebase

firebase_config = {
    "apiKey": "AIzaSyCUW_tZ5vk4zKD2_GGo1-DJ6DfdaKGIXUw",
    "authDomain": "bitpanel-967b1.firebaseapp.com",
    "projectId": "bitpanel-967b1",
    "storageBucket": "bitpanel-967b1.appspot.com",
    "messagingSenderId": "633698121406",
    "appId": "1:633698121406:web:d1e72d97789635135e50ef",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()