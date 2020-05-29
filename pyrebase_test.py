import pyrebase 

config = {
    "apiKey": "AIzaSyB-V0NyRynPW1MXxtmQ5H1kVjGaHZERGLg",
    "authDomain": "movie-recommendor-c013f.firebaseapp.com",
    "databaseURL": "https://movie-recommendor-c013f.firebaseio.com",
    "projectId": "movie-recommendor-c013f",
    "storageBucket": "movie-recommendor-c013f.appspot.com",
    "messagingSenderId": "1016909747943",
    "appId": "1:1016909747943:web:dccf023acb0e09908a3442"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

storage.child("models/1.h5").download(filename='1.h5', path="./temp_models")