from flask import Flask, render_template, request, redirect, session, jsonify
import pickle
import pandas as pd
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


with open("career_data.json") as f:
    career_data = json.load(f)

app = Flask(__name__)
app.secret_key = "aspire_secret_key"

bcrypt = Bcrypt(app)

client = MongoClient(os.environ.get("MONGO_URI"))
db = client["aspire_db"]
users = db["users"]
history = db["history"]


# Load model
model = pickle.load(open("aspire_model.pkl", "rb"))

# Load encoders
target_encoder = pickle.load(open("aspire_encoder.pkl", "rb"))
feature_encoders = pickle.load(open("aspire_feature_encoders.pkl", "rb"))

@app.route('/')
def landing():
    return render_template("landing.html")

#Register
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        # Check password match
        if password != confirm:
            return "Passwords do not match"

        # Check if email already exists
        existing_user = users.find_one({"email": email})

        if existing_user:
            return "Email already registered"

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "password": hashed_pw
            }

        users.insert_one(user_data)

        return redirect('/login')

    return render_template("register.html")

#Login
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):

            session['user'] = email
            session["user_email"] = user["email"]

            return redirect('/home')

        else:
            return "Invalid email or password"

    return render_template("login.html")

#Questionnaire
@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")

#To predict the career 
@app.route("/predict", methods=["POST"])
def predict():

    gender = request.form["gender"]
    ug_course = request.form["ug_course"]
    ug_specialization = request.form["ug_specialization"]
    interests = request.form["interests"]
    skills = request.form["skills"]
    cgpa = request.form["cgpa"]
    certification = request.form["certification"]
    certification_title = request.form.get("certification_title", "None")
    working = request.form["working"]
    masters = request.form["masters"]

    # MANUAL RULES 
    medical_keywords = ["medical", "doctor", "medicine", "biology", "nurse", "pharmacy", "mbbs"]
    law_keywords = ["law", "lawyer", "legal", "advocate", "llb", "judge"]

    text_input = (ug_course + " " + ug_specialization + " " + interests + " " + skills).lower()
    career_override = None

    if any(word in text_input for word in medical_keywords):
        career_override = "Medical"

    elif any(word in text_input for word in law_keywords):
        career_override = "Law"

    #ML PREDICTION
    data = {
        "gender": gender,
        "ug_course": ug_course,
        "ug_specialization": ug_specialization,
        "interests": interests,
        "skills": skills,
        "cgpa": cgpa,
        "certification": certification,
        "certification_title": certification_title,
        "working": working,
        "masters": masters
    }

    df = pd.DataFrame([data])

    # Encode inputs
    for column in df.columns:
        if column in feature_encoders:
            encoder = feature_encoders[column]

            if df[column][0] not in encoder.classes_:
                df[column] = encoder.transform([encoder.classes_[0]])
            else:
                df[column] = encoder.transform(df[column])

    prediction = model.predict(df)
    career = target_encoder.inverse_transform(prediction)[0]
    if career_override:
        career = career_override

    career_map = {
    "Technology": ["Data Scientist", "Software Engineer", "Cybersecurity Analyst"],
    "Business": ["Product Manager", "Business Analyst", "Marketing Manager"],
    "Engineering": ["Mechanical Engineer", "Civil Engineer", "Electrical Engineer"],
    "Medical": ["Doctor", "Surgeon", "Nurse"],
    "Law": ["Lawyer", "Legal Advisor", "Judge"],
    "Education": ["Teacher", "Educational Consultant", "School Administrator"],
    "Unemployed": ["Career Exploration", "Skill Development", "Internships"]
    }
    related = career_map.get(career)
    top3_scores = [92, 88, 84]
    
    top3_results = [
    {"career": related[0], "score": top3_scores[0]},
    {"career": related[1], "score": top3_scores[1]},
    {"career": related[2], "score": top3_scores[2]}
    ]  

    session["last_results"] = top3_results
    session["last_result"] = career

    if 'user' in session:
        history_data = {
            "email": session['user'],
            "date": datetime.now().strftime("%d %B %Y"),
            "results": top3_results
        }
        history.insert_one(history_data)

    return render_template("results.html", career=career, results=top3_results)

#Career Insights
@app.route("/career_insights/<career>")
def career_insights(career):

    career = career.lower().replace(" ", "_")

    data = career_data.get(career)

    if not data:
        return "Career data not found"

    return render_template("career_insights.html", data=data)


@app.route("/career_insights")
def career_redirect():
    return render_template("redirect.html")

#Results
@app.route("/results")
def results_page():

    if "last_results" not in session:
        return redirect("/home")

    return render_template(
        "results.html",
        career=session["last_result"],
        results=session["last_results"]
    )

#History
@app.route('/history')
def history_page():

    if 'user' not in session:
        return redirect('/login')

    user_history = history.find(
        {"email": session['user']}
    ).sort("date", -1)

    return render_template(
        "history.html",
        history=user_history
    )

#Homepage
@app.route('/home')
def home():

    if 'user' not in session:
        return redirect('/login')

    user = users.find_one({"email": session['user']})

    # Get latest assessment
    latest = history.find_one(
        {"email": session['user']},
        sort=[("date", -1)]
    )

    # Get all previous assessments
    assessments = list(history.find(
        {"email": session['user']}
    ).sort("date", -1))

    return render_template(
        "home.html",
        user=user,
        latest=latest,
        assessments=assessments
    )

#Logout
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

#Profile pop-up update
@app.route("/update_profile", methods=["POST"])
def update_profile():

    name = request.form["name"]
    phone = request.form["phone"]
    
    users.update_one(
        {"email": session["user_email"]},
        {"$set": {
            "name": name,
            "phone": phone
        }}
    )

    return redirect("/home")

#Chatbot
@app.route("/chatbot", methods=["POST"])
def chatbot():

    user_message = request.json["message"]

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an AI career advisor for the AspIre platform. Give short helpful answers in 1 or 2 sentences."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = completion.choices[0].message.content

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)