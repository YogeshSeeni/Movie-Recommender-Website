import numpy as np
from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import hashlib
from data_collection import movie_info, popular_movies, random_movie
from model_training.model import create_model, train_model, predict
import pyrebase
from config import config # Contains Firebase Secret Keys
import os
import tensorflow.keras as keras

app = Flask(__name__)


app.permanent_session_lifetime = timedelta(days=365)
app.secret_key = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

users_db = SQLAlchemy(app)

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

class User(users_db.Model):
    id = users_db.Column(users_db.Integer, primary_key=True)
    name = users_db.Column(users_db.String(80))
    email = users_db.Column(users_db.String(80))
    password = users_db.Column(users_db.String(50))
    model_status = users_db.Column(users_db.Boolean, default=False)
    date_created = users_db.Column(users_db.DateTime, default=datetime.now)

@app.route('/')
def home():
    if 'user_name' in session or 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_email = request.form['email']
        user_password = request.form['password']
        user_confirm_password = request.form['confirmPassword']
        user_name = request.form['name']
        if user_password == user_confirm_password:
            check = User.query.filter_by(email=user_email).first()
            if check is None:
                password = hashlib.sha256(user_password.encode())
                user = User(name=user_name, email=user_email, password=password.hexdigest())
                users_db.session.add(user)
                users_db.session.commit()
                flash('Account Created', 'success')
                return redirect(url_for('login'))
                
            if check:
                flash('Email Taken', 'danger')
                return render_template('register.html')
        if user_confirm_password != user_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')
        return render_template('register.html')
    else:
        return render_template('register.html')

@app.route('/login', methods=["POST", "GET"])
def login(accountstatus=False):
    if request.method == "POST":
        user_email = request.form['email']
        user_password = request.form['password']
        perm_session = request.form.getlist('remember')
        print(perm_session)
        user_login_attempt = User.query.filter_by(email=user_email).first()
        user_password_attempt = hashlib.sha256(user_password.encode())
        try:
            if user_password_attempt.hexdigest() == user_login_attempt.password:
                if 'on' in perm_session:
                    session.permanent = True
                    session['user_name'] = user_login_attempt.name
                    session['user_id'] = user_login_attempt.id
                    return redirect(url_for('dashboard'))
                else:
                    session['user_name'] = user_login_attempt.name
                    session['user_id'] = user_login_attempt.id
                    return redirect(url_for('dashboard'))
            else:
                flash("Email or Password did not match", "danger")
                return render_template("login.html")
        except:
            flash("Email or Password did not match", "danger")
            return render_template("login.html")
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_name' in session and 'user_id' in session:
        authenticated_user = User.query.filter_by(id=int(session.get('user_id'))).first()
        return render_template('dashboard.html', status=authenticated_user.model_status)
    else:
        return redirect(url_for('home'))
        
@app.route('/logout')
def logout():
    if 'user_name' in session or 'user_id' in session:
        session.pop('user_name', None)
        session.pop("user_id", None)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

global movie_counter, positive_reviews, negative_reviews, X, y
movie_counter = 0
positive_reviews = 0
negative_reviews = 0
X = []
y= []

@app.route('/train', methods=['GET', 'POST'])
def train():
    global movie_counter, positive_reviews, negative_reviews, X, y
    popular_movies_list = popular_movies.get_popular_movies()
    if 'user_name' in session and 'user_id' in session:
        if request.method == 'POST':
            if 'idk' in request.form['submit_button']:
                movie_counter += 1
                return render_template('train.html', positive_reviews=positive_reviews, negative_reviews=negative_reviews, ui=movie_info.get_movie_ui(popular_movies_list[movie_counter]))
            if 'no'in request.form['submit_button']:
                try:
                    if negative_reviews < 5:
                        X.append(movie_info.get_movie_info(popular_movies_list[movie_counter]))
                        y.append(0)
                except:
                    negative_reviews -= 1
                movie_counter += 1
                negative_reviews += 1
                if positive_reviews >= 5 and negative_reviews >= 5:
                    model = create_model()
                    model = train_model(model, X, y)
                    model.save(str(session.get('user_id')) + '.h5')
                    storage.child("models/" + str(session.get('user_id')) + '.h5').put(str(session.get('user_id')) + '.h5')

                    model_made_user = User.query.filter_by(id=int(session.get('user_id'))).update(dict(model_status=True))
                    users_db.session.commit()

                    return redirect(url_for('dashboard'))
                return render_template('train.html', positive_reviews=positive_reviews, negative_reviews=negative_reviews, ui=movie_info.get_movie_ui(popular_movies_list[movie_counter]))
            if 'yes'in request.form['submit_button']:
                try:
                    if positive_reviews < 5:
                        X.append(movie_info.get_movie_info(popular_movies_list[movie_counter]))
                        y.append(1)
                except:
                    positive_reviews -= 1
                movie_counter += 1
                positive_reviews += 1
                if positive_reviews >= 5 and negative_reviews >= 5:
                    model = create_model()
                    model = train_model(model, X, y)
                    model.save(str(session.get('user_id')) + '.h5')
                    storage.child("models/" + str(session.get('user_id')) + '.h5').put(str(session.get('user_id')) + '.h5')
                    os.remove(str(session.get('user_id')) + '.h5')
                    return redirect(url_for('dashboard'))
                return render_template('train.html', positive_reviews=positive_reviews, negative_reviews=negative_reviews, ui=movie_info.get_movie_ui(popular_movies_list[movie_counter]))
        return render_template('train.html', positive_reviews=positive_reviews, negative_reviews=negative_reviews, ui=movie_info.get_movie_ui(popular_movies_list[0]))
    else:
        negative_reviews = 0
        positive_reviews = 0
        X = []
        y = []
        return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    if request.method == 'POST':
        storage.child("models/" + str(session.get('user_id')) + '.h5').download(filename=str(session.get('user_id')) + '.h5', path="/")
        model = keras.models.load_model(str(session.get('user_id')) + '.h5')
        while True:
            try:
                rand_movie = random_movie.get_random_movie()
                prediction = model.predict([movie_info.get_movie_info(rand_movie)])
                if prediction[0][0] >= 0.5:
                    os.remove(str(session.get('user_id')) + '.h5')
                    return render_template('predict.html', prediction=prediction, ui=movie_info.get_movie_ui(rand_movie))
            except:
                continue
    if 'user_name' in session and 'user_id' in session:
        authenticated_user = User.query.filter_by(id=int(session.get('user_id'))).first()
        return render_template('predicthome.html', status=authenticated_user.model_status)
    else:
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
