# AspIre

An AI-powered career guidance web application that helps students discover their ideal career path based on their academic background, skills, and interests.

## Features

- **AI Career Matching** — ML model predicts the best-fit career domain from user inputs
- **Career Insights** — Detailed pages with skills, roadmap, courses, and demand info per career
- **Assessment History** — Logged results per user, viewable anytime
- **User Auth** — Secure registration and login with bcrypt password hashing
- **Chatbot UI** — Embedded career Q&A assistant on the home page

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, Jinja2 |
| Database | MongoDB Atlas |
| ML Model | scikit-learn (pickle) |
| Auth | Flask-Bcrypt |

## Project Structure
```
AspIre/
├── app.py                        # Main Flask application
├── aspire_model.pkl              # Trained ML model
├── aspire_encoder.pkl            # Target label encoder
├── aspire_feature_encoders.pkl   # Feature encoders
├── static/
│   ├── css/                      # Page stylesheets
│   ├── images/                   # Icons and backgrounds
│   └── home.js                   # Frontend JS
└── templates/                    # Jinja2 HTML templates
    ├── landing.html
    ├── login.html
    ├── register.html
    ├── home.html
    ├── questionnaire.html
    ├── results.html
    ├── career_insights.html
    ├── history.html
    └── redirect.html
```

## Setup

1. **Clone the repository**
```bash
   git clone https://github.com/your-username/aspire.git
   cd aspire
```

2. **Install dependencies**
```bash
   pip install flask flask-bcrypt pymongo pandas scikit-learn
```

3. **Configure MongoDB**
   Update the connection string in `app.py`:
```python
   client = MongoClient("your-mongodb-connection-string")
```

4. **Run the app**
```bash
   python app.py
```

5. Open `http://localhost:5000` in your browser.

## Career Domains

The model predicts one of the following career domains:

`Technology` · `Business` · `Education` · `Medical` · `Law` · `Engineering` · `Unemployed`

Each domain maps to specific career roles with dedicated insights pages.

## ML Model

The model uses a supervised classification approach trained on student profile data. Inputs include:

- Gender, UG course & specialization
- Primary interests and skills
- CGPA range
- Certifications, work experience, and Masters plans

Manual keyword rules override the model for medical and law-related inputs.

## Routes

| Route | Description |
|---|---|
| `/` | Landing page |
| `/register` | User registration |
| `/login` | User login |
| `/home` | Dashboard |
| `/questionnaire` | Career assessment form |
| `/predict` | ML prediction endpoint (POST) |
| `/results` | Assessment results |
| `/career_insights/<career>` | Detailed career info |
| `/history` | Past assessments |
| `/logout` | End session |
