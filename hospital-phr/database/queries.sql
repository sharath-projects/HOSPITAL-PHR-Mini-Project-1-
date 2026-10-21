-- queries.sql : the 8 queries the app needs (? = placeholder, never join text into SQL)

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
