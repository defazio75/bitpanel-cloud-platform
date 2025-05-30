import pyrebase

# 🔑 Required for authentication
firebase_api_key = "AIzaSyCUW_tZ5vk4zKD2_GGo1-DJ6DfdaKGIXUw"

# 🌐 Firebase project configuration
firebase_project_info = {
    "apiKey": firebase_api_key,
    "authDomain": "bitpanel-967b1.firebaseapp.com",
    "databaseURL": "https://bitpanel-967b1-default-rtdb.firebaseio.com/",
    "projectId": "bitpanel-967b1",
    "storageBucket": "bitpanel-967b1.appspot.com",
    "messagingSenderId": "633698121406",
    "appId": "1:633698121406:web:d1e72d97789635135e50ef"
}

# ✅ Initialize and export the firebase object
firebase = pyrebase.initialize_app(firebase_project_info)
auth = firebase.auth()
