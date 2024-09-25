import sqlite3
from faker import Faker

# Create a Faker instance with locale set to 'en_SG' for Singapore or 'en_AS' for Asian names.
fake = Faker("en_US")

# Database connection
conn = sqlite3.connect("./databases/healthcare.db")
cursor = conn.cursor()


# New function to generate user data
def generate_users():
    # Manually defined Admin users
    admin_users = [
        (
            "Srinath",  # First name
            "Sridharan",  # Last name
            "srinath.admin",  # Username
            "srinath@example.com",  # Email
            "1234567890",  # Phone number
            "password1",  # Password
            "Admin",  # Register type
        ),
        (
            "Chester",  # First name
            "Low",  # Last name
            "chester.low",  # Username
            "chester.admin@example.com",  # Email
            "0987654321",  # Phone number
            "password2",  # Password
            "Admin",  # Register type
        ),
    ]

    # Generate 5 Doctor/Nurse users
    professional_users = [
        (
            fake.first_name(),  # First name
            fake.last_name(),  # Last name
            fake.user_name(),  # Username
            fake.email(),  # Email
            fake.phone_number(),  # Phone number
            "password3",  # Password
            "Doctor/Nurse",  # Register type
        )
        for _ in range(5)
    ]

    # Generate 23 Patient users
    patient_users = [
        (
            fake.first_name(),  # First name
            fake.last_name(),  # Last name
            fake.user_name(),  # Username
            fake.email(),  # Email
            fake.phone_number(),  # Phone number
            "password4",  # Password
            "Patient",  # Register type
        )
        for _ in range(23)
    ]

    # Combine all users into one list
    users = admin_users + professional_users + patient_users

    cursor.executemany(
        """
        INSERT INTO User (first_name, last_name, username, email, phone_number, password, register_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        users,
    )
    conn.commit()


# Insert sample data into Patient_Info table for 25 patients
def populate_patient_info():
    diagnoses = [
        "Stage 1 Invasive Ductal Carcinoma",
        "Stage 2 Lobular Carcinoma",
        "DCIS (Ductal Carcinoma In Situ)",
        "Triple-Negative Breast Cancer",
        "Her2-Positive Breast Cancer",
        "Chronic Hypertension",
        "Diabetes Mellitus Type 2",
        "Osteoporosis",
        "Obesity",
        "Asthma",
    ]

    treatment_types = [
        "Chemotherapy",
        "Radiation Therapy",
        "Mastectomy",
        "Lumpectomy",
        "Hormone Therapy",
        "Targeted Therapy",
        "Blood Pressure Medication",
        "Insulin Therapy",
        "Calcium Supplement",
        "Bronchodilator Inhaler",
    ]

    treatment_descriptions = [
        "Administered Adriamycin and Cyclophosphamide followed by Paclitaxel.",
        "Underwent mastectomy with sentinel lymph node biopsy.",
        "Completed 5 weeks of radiation therapy to the left breast.",
        "Taking Tamoxifen for estrogen receptor-positive breast cancer.",
        "Started Herceptin for Her2-positive breast cancer.",
        "On Lisinopril for management of chronic hypertension.",
        "Insulin dose adjusted based on recent HbA1c levels.",
        "Patient is on Alendronate for osteoporosis management.",
        "Prescribed weight loss management plan including diet and exercise.",
        "Using Symbicort inhaler daily for asthma control.",
    ]

    progress_notes = [
        "Patient reports mild nausea post-chemotherapy, managed with antiemetics.",
        "Surgical site healing well, no signs of infection or lymphedema.",
        "Patient experiencing hot flashes and mood swings due to hormone therapy.",
        "Follow-up mammogram scheduled in 6 months to monitor for recurrence.",
        "Patient reports fatigue and mild neuropathy, likely side effects of chemotherapy.",
        "Blood pressure under control, advised to continue current medication.",
        "Patient reports improved glycemic control, no hypoglycemic episodes noted.",
        "Bone density stable on current therapy, no new fractures reported.",
        "Weight loss achieved as per plan, advised to maintain current regimen.",
        "Asthma symptoms well-controlled with current medication, no exacerbations.",
    ]

    patient_info = [
        (
            userID,
            fake.random_int(min=55, max=100),  # Generate random age between 55 and 90
            fake.random_element(elements=diagnoses),  # Choose a random diagnosis
            fake.random_element(
                elements=treatment_types
            ),  # Choose a random treatment type
            fake.random_element(
                elements=treatment_descriptions
            ),  # Choose a random treatment description
            round(
                fake.random_number(digits=1, fix_len=False) / 10.0, 1
            ),  # Bone mass density example
            fake.random_element(
                elements=progress_notes
            ),  # Choose a random progress note
        )
        for userID in range(3, 28)  # Skipping userID 1 and 2 as they are Admins
    ]

    cursor.executemany(
        """
        INSERT INTO Patient_Info (userID, age, diagnosis, treatment_type, treatment_description, bone_mass_density, progress_note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        patient_info,
    )
    conn.commit()


# Insert sample data into Medication table for 25 patients
# Insert sample data into Medication table for 25 patients
# Insert sample data into Medication table for 25 patients with an extensive pool of medications
def populate_medication():
    # Define a comprehensive mapping of medications to their corresponding conditions
    medication_condition_map = {
        # Breast Cancer Medications
        "Tamoxifen": "Breast Cancer (Hormone Therapy)",
        "Letrozole": "Breast Cancer (Hormone Therapy)",
        "Anastrozole": "Breast Cancer (Hormone Therapy)",
        "Exemestane": "Breast Cancer (Hormone Therapy)",
        "Trastuzumab": "Breast Cancer (HER2-Positive)",
        "Pertuzumab": "Breast Cancer (HER2-Positive)",
        "Doxorubicin": "Breast Cancer (Chemotherapy)",
        "Cyclophosphamide": "Breast Cancer (Chemotherapy)",
        "Paclitaxel": "Breast Cancer (Chemotherapy)",
        "Docetaxel": "Breast Cancer (Chemotherapy)",
        # General Medications
        "Insulin": "Diabetes",
        "Metformin": "Diabetes",
        "Lisinopril": "Hypertension",
        "Amlodipine": "Hypertension",
        "Albuterol": "Asthma",
        "Fluticasone": "Asthma",
        "Calcium": "Osteoporosis",
        "Vitamin D": "Osteoporosis",
        "Ibuprofen": "Chronic Pain",
        "Aspirin": "Chronic Pain",
        "Paracetamol": "Pain Relief",
        "Omeprazole": "Gastroesophageal Reflux Disease (GERD)",
        "Atorvastatin": "High Cholesterol",
        "Levothyroxine": "Hypothyroidism",
        "Warfarin": "Blood Thinner",
        "Amoxicillin": "Bacterial Infection",
        "Ciprofloxacin": "Bacterial Infection",
        "Prednisone": "Inflammation",
        "Metoprolol": "Hypertension",
        "Losartan": "Hypertension",
    }

    medications = []
    for userID in range(3, 28):  # Skipping userID 1 and 2 as they are Admins
        # Random number of medications for each patient (between 1 and 3)
        num_medications = fake.random_int(min=1, max=3)
        for _ in range(num_medications):
            medication_name = fake.word(
                ext_word_list=list(medication_condition_map.keys())
            )
            medication_condition = medication_condition_map[
                medication_name
            ]  # Get the corresponding condition
            medications.append(
                (
                    medication_name,
                    fake.word(
                        ext_word_list=["Tablet", "Injection", "Inhaler", "Supplement"]
                    ),
                    userID,
                    None,  # Assuming no file path is needed
                    fake.date_this_year(),
                    medication_condition,  # Use the mapped condition instead of a random sentence
                    fake.word(
                        ext_word_list=[
                            "Nausea",
                            "Dizziness",
                            "Throat irritation",
                            "Low blood sugar",
                            "Stomach upset",
                            "None",
                        ]
                    ),
                )
            )

    cursor.executemany(
        """
        INSERT INTO Medication (medication_name, medication_type, userID, file_path, date_medication_prescribed, medication_treatment_used, side_effect)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        medications,
    )
    conn.commit()


# Insert sample data into Image table for 25 patients
def populate_images():
    images = [
        (
            userID,
            f"/path/to/image{userID-2}.jpg",  # Creating unique file paths for each patient
            fake.date_this_year(),
        )
        for userID in range(3, 28)  # Skipping userID 1 and 2 as they are Admins
    ]
    cursor.executemany(
        """
        INSERT INTO Image (userID, file_path, date_uploaded)
        VALUES (?, ?, ?)
    """,
        images,
    )
    conn.commit()


# Insert sample data into Appointment table for 25 patients
def populate_appointments():
    appointments = [
        (
            userID,
            fake.word(
                ext_word_list=[
                    "Medication",
                    "Physical Therapy",
                    "Inhaler",
                    "Treatment",
                    "Surgery",
                ]
            ),
            fake.word(
                ext_word_list=["Checkup", "Follow-up", "Consultation", "Procedure"]
            ),
            fake.date_this_year(),
            fake.time(),
            fake.date_this_year(),
            fake.time(),
            fake.date_this_year(),
            fake.time(),
        )
        for userID in range(3, 28)  # Skipping userID 1 and 2 as they are Admins
    ]
    cursor.executemany(
        """
        INSERT INTO Appointment (userID, treatment_type, appointment_type, appointment_date, appointment_time, preop_date, preop_time, postop_date, postop_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        appointments,
    )
    conn.commit()


# Modify the populate_all function to include the new user generation
def populate_all():
    generate_users()  # Populate users with the new function
    populate_patient_info()
    populate_medication()
    populate_images()
    populate_appointments()
    print("Data population complete.")


if __name__ == "__main__":
    populate_all()

# Close the connection
conn.close()
