-- seed.sql : FAKE demo data only. The 2 users are created by app.py.
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
