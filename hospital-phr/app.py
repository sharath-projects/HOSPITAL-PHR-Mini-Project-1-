# ==== STAGE 1: setup, database helper, first run ====
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
    """One database connection per request."""
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
    """Create hospital.db from the SQL files and add the 2 demo users."""
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
    """'Drug A, Drug B + Drug C' -> ['Drug A', 'Drug B', 'Drug C']"""
    return [d.strip() for d in re.split(r"[,;+\n]", text) if d.strip()]


def find_allergy(drug_text, allergies):
    """Return (drug, allergy) for the first match, or None if all drugs look safe."""
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
