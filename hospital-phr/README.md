# Patient Health Record Management System with Risk-Based Allergy Warning
A college mini project. FAKE DATA ONLY. Not a certified medical system.

## Features
Login (doctor / receptionist), add / search / view patients, record allergies and visits,
risk-based allergy screening (Minor: verbal question; Major: allergy test status),
and a red warning when a prescribed drug matches a recorded allergy.

## Run
python -m venv venv
venv\Scripts\activate            (Windows)     source venv/bin/activate   (Mac / Linux)
pip install -r requirements.txt
python app.py
Open http://127.0.0.1:5000

Demo logins (fake): doctor1 / doctor123 (doctor), reception1 / recep123 (receptionist)
Reset all data: stop the app, delete hospital.db, start again.

## Known limitations
Drug matching is by text only: brand names, drug families and spelling mistakes are not detected.
Two roles only. No audit log. Use fake data only.
