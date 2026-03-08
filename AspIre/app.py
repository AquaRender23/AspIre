from flask import Flask, render_template, request, redirect, session
import pickle
import pandas as pd
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "aspire_secret_key"

bcrypt = Bcrypt(app)

client = MongoClient("mongodb+srv://AspIre_admin:MrUR5W2KhamcC29C@aspire.p7uyq5d.mongodb.net/?appName=AspIre")
db = client["aspire_db"]
users = db["users"]
history = db["history"]


# Load model
model = pickle.load(open("aspire_model.pkl", "rb"))

# Load encoders
target_encoder = pickle.load(open("aspire_encoder.pkl", "rb"))
feature_encoders = pickle.load(open("aspire_feature_encoders.pkl", "rb"))

#Dictionary
career_data = {

"data_scientist": {
"title": "Data Scientist",
"description": "Analyze complex datasets to extract insights and help organizations make data-driven decisions.",
"skills": ["Python", "Machine Learning", "Statistics", "Data Visualization"]
},

"software_engineer": {
"title": "Software Engineer",
"description": "Design and build software applications and systems used across industries.",
"skills": ["Programming", "Algorithms", "Databases", "System Design"]
},

"cybersecurity_analyst": {
"title": "Cybersecurity Analyst",
"description": "Protect networks, systems and data from cyber threats and attacks.",
"skills": ["Network Security", "Ethical Hacking", "Risk Analysis", "Cryptography"]
},

"entrepreneur": {
"title": "Entrepreneur",
"description": "Build and manage businesses by turning innovative ideas into products or services.",
"skills": ["Leadership", "Business Strategy", "Finance", "Innovation"]
},

"business_analyst": {
"title": "Business Analyst",
"description": "Analyze business processes and help organizations improve efficiency and decision-making.",
"skills": ["Data Analysis", "Problem Solving", "Communication", "Business Strategy"]
},

"marketing_manager": {
"title": "Marketing Manager",
"description": "Develop strategies to promote products and services and reach customers effectively.",
"skills": ["Marketing Strategy", "Communication", "Market Research", "Branding"]
},

"teacher": {
"title": "Teacher",
"description": "Educate students and help them develop knowledge and skills for the future.",
"skills": ["Communication", "Subject Knowledge", "Patience", "Teaching Methods"]
},

"educational_consultant": {
"title": "Educational Consultant",
"description": "Guide students and institutions on academic programs, learning strategies and career planning.",
"skills": ["Advising", "Education Planning", "Communication", "Research"]
},

"school_administrator": {
"title": "School Administrator",
"description": "Manage schools and educational institutions, ensuring smooth academic operations.",
"skills": ["Leadership", "Management", "Communication", "Organization"]
},

"doctor": {
"title": "Doctor",
"description": "Diagnose illnesses and treat patients to improve overall health and wellbeing.",
"skills": ["Medical Knowledge", "Patient Care", "Diagnosis", "Communication"]
},

"surgeon": {
"title": "Surgeon",
"description": "Perform surgical operations to treat injuries, diseases and health conditions.",
"skills": ["Surgery", "Precision", "Decision Making", "Medical Knowledge"]
},

"nurse": {
"title": "Nurse",
"description": "Provide patient care, assist doctors and monitor recovery of patients.",
"skills": ["Patient Care", "Medical Knowledge", "Compassion", "Communication"]
},

"lawyer": {
"title": "Lawyer",
"description": "Represent clients and provide legal advice in legal matters and court cases.",
"skills": ["Legal Research", "Negotiation", "Public Speaking", "Critical Thinking"]
},

"legal_advisor": {
"title": "Legal Advisor",
"description": "Guide organizations and individuals on legal issues and compliance.",
"skills": ["Legal Knowledge", "Problem Solving", "Negotiation", "Communication"]
},

"judge": {
"title": "Judge",
"description": "Preside over court proceedings and deliver fair judgments based on law.",
"skills": ["Legal Expertise", "Decision Making", "Ethics", "Critical Thinking"]
},

"police_officer": {
"title": "Police Officer",
"description": "Maintain law and order, investigate crimes and protect public safety.",
"skills": ["Law Enforcement", "Physical Fitness", "Investigation", "Decision Making"]
},

"detective": {
"title": "Detective",
"description": "Investigate complex criminal cases and gather evidence to solve crimes.",
"skills": ["Investigation", "Observation", "Critical Thinking", "Problem Solving"]
},

"mechanical_engineer": {
"title": "Mechanical Engineer",
"description": "Design and develop machines and mechanical systems used in industries.",
"skills": ["Engineering Design", "Physics", "Problem Solving", "CAD"]
},

"civil_engineer": {
"title": "Civil Engineer",
"description": "Design and construct infrastructure such as roads, bridges and buildings.",
"skills": ["Structural Design", "Project Management", "Mathematics", "Engineering"]
},

"electrical_engineer": {
"title": "Electrical Engineer",
"description": "Develop electrical systems, circuits and power technologies.",
"skills": ["Electronics", "Circuits", "Power Systems", "Problem Solving"]
},

"career_exploration": {
"title": "Career Exploration",
"description": "You may still be exploring different career paths and interests.",
"skills": ["Self Learning", "Exploration", "Skill Development", "Research"]
},

"skill_development": {
"title": "Skill Development",
"description": "Building skills through certifications, courses and projects to improve career opportunities.",
"skills": ["Learning", "Practice", "Adaptability", "Growth Mindset"]
},

"internships": {
"title": "Internships",
"description": "Gain practical work experience to discover strengths and explore industries.",
"skills": ["Teamwork", "Communication", "Learning", "Work Experience"]
}

}

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

            return redirect('/home')

        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")

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

    # ---------- MANUAL RULES ----------
    medical_keywords = ["medical", "doctor", "medicine", "biology", "nurse", "pharmacy", "mbbs"]
    law_keywords = ["law", "lawyer", "legal", "advocate", "llb", "judge"]

    text_input = (ug_course + " " + ug_specialization + " " + interests + " " + skills).lower()

    if any(word in text_input for word in medical_keywords):
        return render_template("results.html", career="Medical")

    if any(word in text_input for word in law_keywords):
        return render_template("results.html", career="Law")

    # ---------- ML PREDICTION ----------

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

    session["last_result"] = career

    related_careers = {
        "data_scientist": ["Software Engineer", "AI Engineer"],
        "software_engineer": ["Product Manager", "Data Scientist"],
        "business_analyst": ["Product Manager", "UX Designer"],
        "cybersecurity_analyst": ["Ethical Hacker", "Network Engineer"],
        "lawyer": ["Legal Advisor", "Judge"],
        "doctor": ["Surgeon", "Medical Researcher"]
        }

    related = related_careers.get(career, ["Career Option 2", "Career Option 3"])

    if 'user' in session:
        history_data = {
            "email": session['user'],

            "top1": career,
            "score1": 92,

            "top2": "related[0]",
            "score2": 87,

            "top3": "related[1]",
            "score3": 85,

            "date": datetime.now()
        }

        history.insert_one(history_data)

    return render_template("results.html", career=career)

@app.route('/career_insights/<career>')
def career_insights(career):

    data = career_data.get(career)

    return render_template("career_insights.html", data=data)

@app.route("/results")
def results():

    if "last_result" not in session:
        return redirect("/questionnaire")

    career = session["last_result"]

    return render_template("results.html", career=career)

@app.route("/career_insights")
def career_redirect():
    return render_template("redirect.html")

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

@app.route('/home')
def home():

    if 'user' not in session:
        return redirect('/login')

    user = users.find_one({"email": session['user']})

    return render_template("home.html", user=user)


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)