-- schema.sql : creates the 4 tables
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
