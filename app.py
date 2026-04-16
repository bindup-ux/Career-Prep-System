from flask import Flask, render_template, request, redirect
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}
global_skills = []
global_questions = []

# -------- EXTRACT TEXT --------
def extract_text(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

# -------- SKILL EXTRACTION --------
def extract_skills(text):
    skills = ["python", "java", "html", "css", "javascript", "sql"]
    found = []
    for s in skills:
        if s in text:
            found.append(s)
    return found

# -------- QUESTION GENERATION --------
def generate_questions(skills):
    questions = []

    question_bank = {
        "python": ["Explain OOP in Python", "What are decorators?"],
        "java": ["Explain JVM", "What is inheritance?"],
        "html": ["What is semantic HTML?"],
        "css": ["Explain flexbox"],
        "javascript": ["What is closure?"],
        "sql": ["What is normalization?"]
    }

    for skill in skills:
        if skill in question_bank:
            questions.extend(question_bank[skill])

    return questions

# -------- EVALUATION --------
def evaluate_answer(ans):
    keywords = ["example", "definition", "use", "class", "object", "method"]

    score = sum(1 for k in keywords if k in ans.lower())

    if score >= 3:
        return score, "Excellent 🔥"
    elif score == 2:
        return score, "Good 👍"
    else:
        return score, "Improve ❗"

# -------- ROUTES --------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST'])
def signup():
    users[request.form['username']] = request.form['password']
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    u = request.form['username']
    p = request.form['password']
    if u in users and users[u] == p:
        return redirect('/dashboard')
    return "Invalid Login"

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/resume')
def resume():
    return render_template("resume.html", skills=None)

@app.route('/analyze', methods=['POST'])
def analyze():
    global global_skills, global_questions

    file = request.files['resume']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = extract_text(path)
    global_skills = extract_skills(text)
    global_questions = generate_questions(global_skills)

    return render_template("resume.html", skills=global_skills)

@app.route('/qa')
def qa():
    return render_template("qa.html", questions=global_questions)

# ✅ THIS WAS MISSING — NOW FIXED
@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    if request.method == 'POST':
        answers = request.form.getlist('answers')

        results = []
        total = 0

        for ans in answers:
            score, fb = evaluate_answer(ans)
            total += score
            results.append({"score": score, "fb": fb})

        return render_template("evaluation.html", results=results, total=total)

    return render_template("evaluation.html", results=[], total=0)

@app.route('/resources')
def resources():
    return render_template("resources.html")

if __name__ == "__main__":
    app.run(debug=True)