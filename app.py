from flask import Flask, request, render_template, redirect, session
import numpy as np
import pandas as pd
import pickle
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Load the machine learning model
model = pickle.load(open('model.pickle', 'rb'))

# User data storage path
USER_DATA_FILE = 'users.json'

# Load user data
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USER_DATA_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def home_page():
    return render_template('home.html')  # Renders the home page

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/index')  # Redirect to the main page after successful login
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username not in users:
            users[username] = {'password': password}
            save_users(users)
            return redirect('/login.html')
        else:
            error = 'Username already exists.'
            return render_template('register.html', error=error)

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')  # Protect the main page, redirect if not logged in
    return render_template('index.html')  # Render the main page after login

@app.route('/result', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect('/login')

    if request.method == "POST":
        # Collect input features
        
        gender_Male = int(request.form['gender'])
        age = int(request.form['age'])
        hypertension_1 = int(request.form['hypertension'])
        heart_disease_1 = int(request.form['disease'])
        ever_married_Yes = int(request.form['married'])
        work = int(request.form['work'])
        Residence_type_Urban = int(request.form['residence'])
        avg_glucose_level = float(request.form['avg_glucose_level'])
        bmi = float(request.form['bmi'])
        smoking = int(request.form['smoking'])

        # Work type encoding
        work_type_Never_worked = 1 if work == 1 else 0
        work_type_Private = 1 if work == 2 else 0
        work_type_Self_employed = 1 if work == 3 else 0
        work_type_children = 1 if work == 4 else 0

        # Smoking status encoding
        smoking_status_formerly_smoked = 1 if smoking == 1 else 0
        smoking_status_never_smoked = 1 if smoking == 2 else 0
        smoking_status_smokes = 1 if smoking == 3 else 0

        input_features = [age, avg_glucose_level, bmi, gender_Male, hypertension_1,
                          heart_disease_1, ever_married_Yes, work_type_Never_worked,
                          work_type_Private, work_type_Self_employed, work_type_children,
                          Residence_type_Urban, smoking_status_formerly_smoked,
                          smoking_status_never_smoked, smoking_status_smokes]

        features_value = [np.array(input_features)]
        features_name = ['age', 'avg_glucose_level', 'bmi', 'gender_Male',
                         'hypertension_1', 'heart_disease_1', 'ever_married_Yes',
                         'work_type_Never_worked', 'work_type_Private',
                         'work_type_Self_employed', 'work_type_children',
                         'Residence_type_Urban', 'smoking_status_formerly_smoked',
                         'smoking_status_never_smoked', 'smoking_status_smokes']

        df = pd.DataFrame(features_value, columns=features_name)
        prediction = model.predict(df)[0]

        if prediction == 1:
            prediction_text = 'Patient has stroke risk'
        else:
            prediction_text = 'Congratulations, patient does not have stroke risk'

        return render_template('index.html', prediction_text=prediction_text)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
