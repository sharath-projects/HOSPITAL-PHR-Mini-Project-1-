import os

FILES = {
    "hospital-phr/requirements.txt": """Flask>=3.0
Werkzeug>=3.0
""",

    "hospital-phr/.gitignore": """venv/
__pycache__/
*.pyc
hospital.db
""",

    "hospital-phr/README.md": """# Patient Health Record Management System with Risk-Based Allergy Warning
A college mini project. FAKE DATA ONLY. Not a certified medical system.

## Features
Login (doctor / receptionist), add / search / view patients, record allergies and visits,
risk-based allergy screening (Minor: verbal question; Major: allergy test status),
and a red warning when a prescribed drug matches a recorded allergy.

## Run
python -m venv venv
venv\\Scripts\\activate            (Windows)     source venv/bin/activate   (Mac / Linux)
pip install -r requirements.txt
python app.py
Open http://127.0.0.1:5000

Demo logins (fake): doctor1 / doctor123 (doctor), reception1 / recep123 (receptionist)
Reset all data: stop the app, delete hospital.db, start again.

## Known limitations
Drug matching is by text only: brand names, drug families and spelling mistakes are not detected.
Two roles only. No audit log. Use fake data only.
""",

    "hospital-phr/database/schema.sql": """-- schema.sql : creates the 4 tables
PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('doctor', 'receptionist'))
);

CREATE TABLE patients (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    age     INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender  TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone   TEXT NOT NULL,
    address TEXT
);

CREATE TABLE allergies (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    substance  TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE visits (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id          INTEGER NOT NULL,
    visit_date          TEXT NOT NULL,
    complaint           TEXT NOT NULL,
    diagnosis           TEXT,
    drug                TEXT NOT NULL,
    case_type           TEXT NOT NULL CHECK (case_type IN ('Minor', 'Major')),
    allergy_asked       INTEGER NOT NULL DEFAULT 1 CHECK (allergy_asked IN (0, 1)),
    allergy_test_status TEXT NOT NULL DEFAULT 'Not applicable'
        CHECK (allergy_test_status IN ('Not applicable', 'Not needed', 'Advised', 'Done')),
    allergy_test_note   TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
""",

    "hospital-phr/database/seed.sql": """-- seed.sql : FAKE demo data only. The 2 users are created by app.py.
INSERT INTO patients (name, age, gender, phone, address) VALUES
 ('Ravi Kumar',    45, 'Male',   '9000000001', 'Ward 12, Demo Nagar'),
 ('Anita Sharma',  32, 'Female', '9000000002', 'Ward 3, Sample Colony'),
 ('Mohammed Ali',  58, 'Male',   '9000000003', 'Ward 7, Test Layout'),
 ('Priya Nair',    27, 'Female', '9000000004', 'Ward 9, Demo Nagar'),
 ('Suresh Reddy',  63, 'Male',   '9000000005', 'Ward 1, Sample Colony'),
 ('Lakshmi Devi',  71, 'Female', '9000000006', 'Ward 5, Test Layout'),
 ('Arjun Singh',   19, 'Male',   '9000000007', 'Ward 2, Demo Nagar'),
 ('Meena Iyer',    40, 'Female', '9000000008', 'Ward 8, Sample Colony'),
 ('Kiran Patil',    8, 'Other',  '9000000009', 'Ward 4, Test Layout'),
 ('Fatima Begum',  52, 'Female', '9000000010', 'Ward 6, Demo Nagar');

INSERT INTO allergies (patient_id, substance) VALUES
 (1, 'Penicillin'), (2, 'Sulfa drugs'), (2, 'Aspirin'), (5, 'Ibuprofen'), (8, 'Amoxicillin');

INSERT INTO visits (patient_id, visit_date, complaint, diagnosis, drug, case_type, allergy_asked, allergy_test_status, allergy_test_note) VALUES
 (1, '2026-08-01', 'Fever and cough',  'Viral fever',      'Paracetamol',  'Minor', 1, 'Not applicable', NULL),
 (1, '2026-08-20', 'Sore throat',      'Throat infection', 'Azithromycin', 'Minor', 1, 'Not applicable', NULL),
 (2, '2026-08-05', 'Headache',         'Migraine',         'Paracetamol',  'Minor', 1, 'Not applicable', NULL),
 (3, '2026-08-07', 'Persistent cough', 'Tuberculosis (demo case)', 'Isoniazid + Rifampicin + Ethambutol', 'Major', 1, 'Done', 'Allergy history reviewed, no reaction recorded (demo)'),
 (4, '2026-08-10', 'Skin rash',        'Mild allergy',     'Cetirizine',   'Minor', 1, 'Not applicable', NULL),
 (5, '2026-08-12', 'Knee pain',        'Arthritis',        'Paracetamol',  'Minor', 1, 'Not applicable', NULL),
 (6, '2026-08-15', 'Weakness',         'Low iron',         'Iron tablets', 'Minor', 1, 'Not applicable', NULL),
 (7, '2026-08-18', 'Stomach ache',     'Gastritis',        'Antacid',      'Minor', 1, 'Not applicable', NULL),
 (8, '2026-08-22', 'Tooth pain',       'Dental infection', 'Metronidazole','Minor', 1, 'Not applicable', NULL),
 (9, '2026-08-25', 'Cold',             'Common cold',      'Saline drops', 'Minor', 1, 'Not applicable', NULL);
""",

    "hospital-phr/database/queries.sql": """-- queries.sql : the 8 queries the app needs (? = placeholder, never join text into SQL)

-- Q1 get_user_by_username      needs: username
SELECT id, username, password_hash, role FROM users WHERE username = ?;

-- Q2 insert_patient            needs: name, age, gender, phone, address
INSERT INTO patients (name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?);

-- Q3 search_patients           needs: '%text%'
SELECT id, name, age, gender, phone FROM patients WHERE name LIKE ? ORDER BY name;

-- Q4 get_patient_by_id         needs: id
SELECT id, name, age, gender, phone, address FROM patients WHERE id = ?;

-- Q5 insert_allergy            needs: patient_id, substance
INSERT INTO allergies (patient_id, substance) VALUES (?, ?);

-- Q6 get_allergies             needs: patient_id
SELECT id, substance FROM allergies WHERE patient_id = ? ORDER BY substance;

-- Q7 insert_visit              needs: patient_id, visit_date, complaint, diagnosis, drug,
--                                     case_type, allergy_asked, allergy_test_status, allergy_test_note
INSERT INTO visits (patient_id, visit_date, complaint, diagnosis, drug, case_type,
                    allergy_asked, allergy_test_status, allergy_test_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);

-- Q8 get_visits                needs: patient_id
SELECT visit_date, complaint, diagnosis, drug, case_type, allergy_test_status, allergy_test_note
FROM visits WHERE patient_id = ? ORDER BY visit_date DESC, id DESC;
""",

    "hospital-phr/app.py": """# ==== STAGE 1: setup, database helper, first run ====
import os
import re
import sqlite3
from datetime import date, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hospital.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.permanent_session_lifetime = timedelta(minutes=30)   # automatic logout


def get_db():
    \"\"\"One database connection per request.\"\"\"
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row          # lets us write row["name"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    \"\"\"Create hospital.db from the SQL files and add the 2 demo users.\"\"\"
    db = sqlite3.connect(DB_PATH)
    for name in ("schema.sql", "seed.sql"):
        with open(os.path.join(BASE_DIR, "database", name), encoding="utf-8") as f:
            db.executescript(f.read())
    users = [("doctor1", "doctor123", "doctor"),
             ("reception1", "recep123", "receptionist")]
    for username, password, role in users:
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role))
    db.commit()
    db.close()


if not os.path.exists(DB_PATH):      # first run: build the database
    init_db()


# ==== STAGE 2: login, logout, roles ====
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Only a %s can do that." % role, "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(                      # Q1
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Wrong username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ==== STAGE 3: patients (add, search, view) ====
def validate_patient(form):
    errors = []
    name = form.get("name", "").strip()
    age = form.get("age", "").strip()
    phone = form.get("phone", "").strip()
    if not name:
        errors.append("Name is required.")
    if not age.isdigit() or not (0 <= int(age) <= 120):
        errors.append("Age must be a number from 0 to 120.")
    if form.get("gender") not in ("Male", "Female", "Other"):
        errors.append("Please choose a gender.")
    if not (phone.isdigit() and len(phone) == 10):
        errors.append("Phone must be exactly 10 digits.")
    return errors


def get_patient(pid):
    return get_db().execute(                          # Q4
        "SELECT id, name, age, gender, phone, address FROM patients WHERE id = ?",
        (pid,)).fetchone()


@app.route("/patients")
@login_required
def patients():
    q = request.args.get("q", "").strip()
    rows = get_db().execute(                          # Q3
        "SELECT id, name, age, gender, phone FROM patients "
        "WHERE name LIKE ? ORDER BY name", ("%" + q + "%",)).fetchall()
    return render_template("patients.html", patients=rows, q=q)


@app.route("/patients/add", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        errors = validate_patient(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("patient_form.html", form=request.form)
        db = get_db()
        cur = db.execute(                             # Q2
            "INSERT INTO patients (name, age, gender, phone, address) "
            "VALUES (?, ?, ?, ?, ?)",
            (request.form["name"].strip(), int(request.form["age"]),
             request.form["gender"], request.form["phone"].strip(),
             request.form.get("address", "").strip()))
        db.commit()
        flash("Patient saved.", "success")
        return redirect(url_for("patient_detail", pid=cur.lastrowid))
    return render_template("patient_form.html", form={})


@app.route("/patients/<int:pid>")
@login_required
def patient_detail(pid):
    patient = get_patient(pid)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients"))
    db = get_db()
    allergies = db.execute(                           # Q6
        "SELECT id, substance FROM allergies WHERE patient_id = ? "
        "ORDER BY substance", (pid,)).fetchall()
    visits = db.execute(                              # Q8
        "SELECT visit_date, complaint, diagnosis, drug, case_type, "
        "allergy_test_status, allergy_test_note FROM visits "
        "WHERE patient_id = ? ORDER BY visit_date DESC, id DESC", (pid,)).fetchall()
    return render_template("patient_detail.html", patient=patient,
                           allergies=allergies, visits=visits)


# ==== STAGE 4: allergies (doctor only) ====
@app.route("/patients/<int:pid>/allergy/add", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_allergy(pid):
    patient = get_patient(pid)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients"))
    if request.method == "POST":
        substance = request.form.get("substance", "").strip()
        if not substance:
            flash("Please type the allergy (drug or substance).", "danger")
        else:
            db = get_db()
            db.execute(                               # Q5
                "INSERT INTO allergies (patient_id, substance) VALUES (?, ?)",
                (pid, substance))
            db.commit()
            flash("Allergy saved.", "success")
            return redirect(url_for("patient_detail", pid=pid))
    return render_template("allergy_form.html", patient=patient)


# ==== STAGE 5: visits, risk-based screening and the allergy warning ====
CASE_TYPES = ("Minor", "Major")
TEST_STATUSES = ("Not needed", "Advised", "Done")


def split_drugs(text):
    \"\"\"'Drug A, Drug B + Drug C' -> ['Drug A', 'Drug B', 'Drug C']\"\"\"
    return [d.strip() for d in re.split(r"[,;+\\n]", text) if d.strip()]


def find_allergy(drug_text, allergies):
    \"\"\"Return (drug, allergy) for the first match, or None if all drugs look safe.\"\"\"
    for drug in split_drugs(drug_text):
        d = drug.lower()
        for a in allergies:
            name = a["substance"].strip().lower()
            if name and (name in d or (len(d) >= 4 and d in name)):
                return (drug, a["substance"])
    return None


def validate_visit(form):
    errors = []
    case_type = form.get("case_type")
    if case_type not in CASE_TYPES:
        errors.append("Choose the case type (Minor or Major).")
    if not form.get("complaint", "").strip():
        errors.append("Complaint is required.")
    if not split_drugs(form.get("drug", "")):
        errors.append("Drug is required.")
    if not form.get("allergy_asked"):
        errors.append("Tick the box to confirm you asked the patient about drug allergies.")
    if case_type == "Major" and form.get("allergy_test_status") not in TEST_STATUSES:
        errors.append("For a Major case, choose the allergy test status.")
    return errors


@app.route("/patients/<int:pid>/visit/add", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_visit(pid):
    patient = get_patient(pid)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients"))
    db = get_db()
    allergies = db.execute(                           # Q6
        "SELECT id, substance FROM allergies WHERE patient_id = ? "
        "ORDER BY substance", (pid,)).fetchall()
    if request.method == "POST":
        form = request.form
        errors = validate_visit(form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("visit_form.html", patient=patient,
                                   allergies=allergies, form=form, warning=None)
        matched = find_allergy(form["drug"], allergies)
        if matched and not form.get("override"):
            return render_template("visit_form.html", patient=patient,
                                   allergies=allergies, form=form,
                                   warning=matched)             # NOT saved yet
        case_type = form["case_type"]
        status = form["allergy_test_status"] if case_type == "Major" else "Not applicable"
        db.execute(                                   # Q7
            "INSERT INTO visits (patient_id, visit_date, complaint, diagnosis, drug, "
            "case_type, allergy_asked, allergy_test_status, allergy_test_note) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (pid, date.today().isoformat(), form["complaint"].strip(),
             form.get("diagnosis", "").strip(), form["drug"].strip(), case_type, 1,
             status, form.get("allergy_test_note", "").strip()))
        db.commit()
        if matched:
            flash("Saved with allergy override (%s matches %s). Please note this in the file."
                  % (matched[0], matched[1]), "warning")
        else:
            flash("Visit saved.", "success")
        if status == "Advised":
            flash("An allergy test was advised but is not recorded as done yet.", "warning")
        return redirect(url_for("patient_detail", pid=pid))
    return render_template("visit_form.html", patient=patient,
                           allergies=allergies, form={}, warning=None)


# ==== STAGE 6: run the app ====
if __name__ == "__main__":
    # host 0.0.0.0 lets a phone on the same Wi-Fi open the site
    app.run(host="0.0.0.0", port=5000, debug=True)
""",

    "hospital-phr/templates/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Hospital PHR{% endblock %}</title>
  <!-- Bootstrap 5 from a CDN (needs internet). For offline use, download bootstrap.min.css
       into static/css/ and use: {{ url_for('static', filename='css/bootstrap.min.css') }} -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
  <nav class="navbar navbar-dark bg-primary">
    <div class="container d-flex flex-wrap align-items-center justify-content-between">
      <a class="navbar-brand" href="{{ url_for('home') }}">Hospital PHR</a>
      {% if session.get('user_id') %}
      <div class="d-flex flex-wrap align-items-center">
        <a class="nav-link text-white px-2" href="{{ url_for('patients') }}">Patients</a>
        <a class="nav-link text-white px-2" href="{{ url_for('add_patient') }}">Add patient</a>
        <a class="nav-link text-white px-2" href="{{ url_for('logout') }}">Logout ({{ session['username'] }})</a>
      </div>
      {% endif %}
    </div>
  </nav>

  <main class="container mt-3 mb-5">
    {% with msgs = get_flashed_messages(with_categories=true) %}
      {% for category, message in msgs %}
        <div class="alert alert-{{ category }}" role="alert">{{ message }}</div>
      {% endfor %}
    {% endwith %}

    {% block content %}{% endblock %}
  </main>
</body>
</html>
""",

    "hospital-phr/templates/login.html": """{% extends "base.html" %}
{% block title %}Login - Hospital PHR{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-12 col-md-6 col-lg-4">
    <div class="card">
      <div class="card-body">
        <h4 class="card-title mb-3">Staff login</h4>
        <form method="POST" action="{{ url_for('login') }}">
          <div class="mb-3">
            <label class="form-label" for="username">Username</label>
            <input class="form-control" type="text" id="username" name="username" required autofocus>
          </div>
          <div class="mb-3">
            <label class="form-label" for="password">Password</label>
            <input class="form-control" type="password" id="password" name="password" required>
          </div>
          <button class="btn btn-primary" type="submit">Log in</button>
        </form>
        <p class="text-muted small mt-3 mb-0">Demo logins: doctor1 / doctor123 and reception1 / recep123 (fake data only).</p>
      </div>
    </div>
  </div>
</div>
{% endblock %}
""",

    "hospital-phr/templates/dashboard.html": """{% extends "base.html" %}
{% block title %}Dashboard - Hospital PHR{% endblock %}
{% block content %}
<h4 class="mb-3">Welcome, {{ session['username'] }} ({{ session['role'] }})</h4>
<div class="row">
  <div class="col-12 col-md-6">
    <div class="card"><div class="card-body">
      <h5 class="card-title">Find a patient</h5>
      <p class="card-text">Search by name and open the patient record.</p>
      <a class="btn btn-primary" href="{{ url_for('patients') }}">Search patients</a>
    </div></div>
  </div>
  <div class="col-12 col-md-6">
    <div class="card"><div class="card-body">
      <h5 class="card-title">New patient</h5>
      <p class="card-text">Register a new patient.</p>
      <a class="btn btn-primary" href="{{ url_for('add_patient') }}">Add patient</a>
    </div></div>
  </div>
</div>
{% endblock %}
""",

    "hospital-phr/templates/patients.html": """{% extends "base.html" %}
{% block title %}Patients - Hospital PHR{% endblock %}
{% block content %}
<h4 class="mb-3">Patients</h4>
<form class="row g-2 mb-3" method="GET" action="{{ url_for('patients') }}">
  <div class="col-12 col-sm-8 col-md-6">
    <input class="form-control" type="text" name="q" value="{{ q }}" placeholder="Search by name">
  </div>
  <div class="col-12 col-sm-4 col-md-3">
    <button class="btn btn-primary" type="submit">Search</button>
  </div>
</form>

{% if patients %}
<div class="table-responsive">
  <table class="table table-striped">
    <thead><tr><th>Name</th><th>Age</th><th>Gender</th><th>Phone</th><th></th></tr></thead>
    <tbody>
      {% for p in patients %}
      <tr>
        <td>{{ p['name'] }}</td>
        <td>{{ p['age'] }}</td>
        <td>{{ p['gender'] }}</td>
        <td>{{ p['phone'] }}</td>
        <td><a class="btn btn-sm btn-outline-primary" href="{{ url_for('patient_detail', pid=p['id']) }}">View</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="alert alert-info">No patients found.</div>
{% endif %}
{% endblock %}
""",

    "hospital-phr/templates/patient_form.html": """{% extends "base.html" %}
{% block title %}Add patient - Hospital PHR{% endblock %}
{% block content %}
<h4 class="mb-3">Add patient</h4>
<form method="POST" action="{{ url_for('add_patient') }}">
  <div class="row">
    <div class="col-12 col-md-6 mb-3">
      <label class="form-label" for="name">Full name</label>
      <input class="form-control" type="text" id="name" name="name" value="{{ form.get('name', '') }}" required>
    </div>
    <div class="col-6 col-md-3 mb-3">
      <label class="form-label" for="age">Age</label>
      <input class="form-control" type="number" id="age" name="age" min="0" max="120" value="{{ form.get('age', '') }}" required>
    </div>
    <div class="col-6 col-md-3 mb-3">
      <label class="form-label" for="gender">Gender</label>
      <select class="form-select" id="gender" name="gender" required>
        <option value="">Choose...</option>
        {% for g in ['Male', 'Female', 'Other'] %}
        <option value="{{ g }}" {% if form.get('gender') == g %}selected{% endif %}>{{ g }}</option>
        {% endfor %}
      </select>
    </div>
  </div>
  <div class="mb-3">
    <label class="form-label" for="phone">Phone (10 digits)</label>
    <input class="form-control" type="tel" id="phone" name="phone" maxlength="10" value="{{ form.get('phone', '') }}" required>
  </div>
  <div class="mb-3">
    <label class="form-label" for="address">Address</label>
    <textarea class="form-control" id="address" name="address" rows="2">{{ form.get('address', '') }}</textarea>
  </div>
  <button class="btn btn-primary" type="submit">Save patient</button>
  <a class="btn btn-outline-secondary" href="{{ url_for('patients') }}">Cancel</a>
</form>
{% endblock %}
""",

    "hospital-phr/templates/patient_detail.html": """{% extends "base.html" %}
{% block title %}{{ patient['name'] }} - Hospital PHR{% endblock %}
{% block content %}
<div class="card">
  <div class="card-body">
    <h4 class="card-title">{{ patient['name'] }}</h4>
    <p class="card-text mb-0">
      Age: {{ patient['age'] }} | Gender: {{ patient['gender'] }} | Phone: {{ patient['phone'] }}<br>
      Address: {{ patient['address'] or '-' }}
    </p>
  </div>
</div>

<div class="card">
  <div class="card-body">
    <h5 class="card-title">Allergies</h5>
    {% if allergies %}
      {% for a in allergies %}
        <span class="badge bg-danger me-1">{{ a['substance'] }}</span>
      {% endfor %}
    {% else %}
      <p class="text-muted mb-2">No allergies recorded.</p>
    {% endif %}
    {% if session.get('role') == 'doctor' %}
      <div class="mt-3">
        <a class="btn btn-sm btn-outline-danger" href="{{ url_for('add_allergy', pid=patient['id']) }}">Add allergy</a>
      </div>
    {% endif %}
  </div>
</div>

<div class="card">
  <div class="card-body">
    <h5 class="card-title">Visits</h5>
    {% if visits %}
    <div class="table-responsive">
      <table class="table table-striped">
        <thead><tr><th>Date</th><th>Case</th><th>Complaint</th><th>Diagnosis</th><th>Drug(s)</th><th>Allergy check</th></tr></thead>
        <tbody>
          {% for v in visits %}
          <tr>
            <td>{{ v['visit_date'] }}</td>
            <td>
              {% if v['case_type'] == 'Major' %}<span class="badge bg-warning text-dark">Major</span>
              {% else %}<span class="badge bg-secondary">Minor</span>{% endif %}
            </td>
            <td>{{ v['complaint'] }}</td>
            <td>{{ v['diagnosis'] or '-' }}</td>
            <td>{{ v['drug'] }}</td>
            <td>
              {% if v['case_type'] == 'Minor' %}Asked verbally
              {% else %}Test: {{ v['allergy_test_status'] }}{% if v['allergy_test_note'] %}<br><small class="text-muted">{{ v['allergy_test_note'] }}</small>{% endif %}
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
      <p class="text-muted">No visits yet.</p>
    {% endif %}
    {% if session.get('role') == 'doctor' %}
      <a class="btn btn-sm btn-primary" href="{{ url_for('add_visit', pid=patient['id']) }}">Add visit</a>
    {% endif %}
  </div>
</div>
<a class="btn btn-outline-secondary" href="{{ url_for('patients') }}">Back to list</a>
{% endblock %}
""",

    "hospital-phr/templates/allergy_form.html": """{% extends "base.html" %}
{% block title %}Add allergy - Hospital PHR{% endblock %}
{% block content %}
<h4 class="mb-3">Add allergy for {{ patient['name'] }}</h4>
<form method="POST" action="{{ url_for('add_allergy', pid=patient['id']) }}">
  <div class="mb-3">
    <label class="form-label" for="substance">Drug or substance</label>
    <input class="form-control" type="text" id="substance" name="substance" placeholder="e.g. Penicillin" required>
  </div>
  <button class="btn btn-danger" type="submit">Save allergy</button>
  <a class="btn btn-outline-secondary" href="{{ url_for('patient_detail', pid=patient['id']) }}">Cancel</a>
</form>
{% endblock %}
""",

    "hospital-phr/templates/visit_form.html": """{% extends "base.html" %}
{% block title %}Add visit - Hospital PHR{% endblock %}
{% block content %}
<h4 class="mb-3">New visit for {{ patient['name'] }}</h4>

{% if allergies %}
<p>Known allergies:
  {% for a in allergies %}<span class="badge bg-danger me-1">{{ a['substance'] }}</span>{% endfor %}
</p>
{% else %}
<div class="alert alert-warning" role="alert">
  No allergies are recorded for this patient. Ask the patient about drug allergies before prescribing,
  and add any allergy first.
  <a href="{{ url_for('add_allergy', pid=patient['id']) }}">Add allergy</a>
</div>
{% endif %}

{% if warning %}
<div class="alert alert-danger allergy-alert" role="alert">
  ALLERGY WARNING: the drug <strong>{{ warning[0] }}</strong> matches the recorded allergy
  <strong>{{ warning[1] }}</strong>. It may cause a reaction. Change the drug, or tick the box
  below to save anyway.
</div>
{% endif %}

<form method="POST" action="{{ url_for('add_visit', pid=patient['id']) }}">
  <div class="mb-3">
    <label class="form-label d-block">Case type</label>
    <div class="form-check form-check-inline">
      <input class="form-check-input" type="radio" name="case_type" id="ct_minor" value="Minor"
             {% if form.get('case_type', 'Minor') == 'Minor' %}checked{% endif %}>
      <label class="form-check-label" for="ct_minor">Minor (fever, cold: verbal allergy question)</label>
    </div>
    <div class="form-check form-check-inline">
      <input class="form-check-input" type="radio" name="case_type" id="ct_major" value="Major"
             {% if form.get('case_type') == 'Major' %}checked{% endif %}>
      <label class="form-check-label" for="ct_major">Major (e.g. cancer, many drugs)</label>
    </div>
  </div>
  <div class="mb-3">
    <label class="form-label" for="complaint">Complaint</label>
    <input class="form-control" type="text" id="complaint" name="complaint" value="{{ form.get('complaint', '') }}" required>
  </div>
  <div class="mb-3">
    <label class="form-label" for="diagnosis">Diagnosis</label>
    <input class="form-control" type="text" id="diagnosis" name="diagnosis" value="{{ form.get('diagnosis', '') }}">
  </div>
  <div class="mb-3">
    <label class="form-label" for="drug">Drug(s) prescribed</label>
    <input class="form-control" type="text" id="drug" name="drug" value="{{ form.get('drug', '') }}" required>
    <div class="form-text">Several drugs: separate with a comma or a plus sign, e.g. Drug A, Drug B</div>
  </div>
  <div class="form-check mb-3">
    <input class="form-check-input" type="checkbox" id="allergy_asked" name="allergy_asked" value="1"
           {% if form.get('allergy_asked') %}checked{% endif %}>
    <label class="form-check-label" for="allergy_asked">I asked the patient about drug allergies.</label>
  </div>
  <div class="card"><div class="card-body">
    <h6 class="card-title">For Major cases only: allergy test status</h6>
    <div class="mb-3">
      <select class="form-select" id="allergy_test_status" name="allergy_test_status">
        <option value="">Choose...</option>
        {% for s in ['Not needed', 'Advised', 'Done'] %}
        <option value="{{ s }}" {% if form.get('allergy_test_status') == s %}selected{% endif %}>{{ s }}</option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label class="form-label" for="allergy_test_note">Test result or reason (optional)</label>
      <input class="form-control" type="text" id="allergy_test_note" name="allergy_test_note" value="{{ form.get('allergy_test_note', '') }}">
    </div>
  </div></div>
  {% if warning %}
  <div class="form-check mb-3">
    <input class="form-check-input" type="checkbox" id="override" name="override" value="1">
    <label class="form-check-label" for="override">I understand the risk. Save this visit anyway.</label>
  </div>
  {% endif %}
  <button class="btn btn-primary" type="submit">Save visit</button>
  <a class="btn btn-outline-secondary" href="{{ url_for('patient_detail', pid=patient['id']) }}">Cancel</a>
</form>
{% endblock %}
""",

    "hospital-phr/static/css/style.css": """/* style.css : small custom styles on top of Bootstrap */
body { background: #f5f7fa; }
.navbar-brand { font-weight: 700; }
.card { margin-bottom: 1rem; }

/* the allergy warning must be impossible to miss */
.allergy-alert {
  font-size: 1.15rem;
  font-weight: 700;
  border-left: 10px solid #b00020;
}

/* phones: full-width buttons and slightly smaller tables */
@media (max-width: 576px) {
  .btn { width: 100%; margin-bottom: 0.5rem; }
  .btn-sm { width: auto; margin-bottom: 0; }
  table { font-size: 0.9rem; }
}
"""
}

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

print("\nAll 16 files created successfully inside the 'hospital-phr' folder!")