import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_id = os.getenv("TELEGRAM_CHAT_ID")

# Telegram token and chat ID
TELEGRAM_BOT_TOKEN = telegram_bot_token
TELEGRAM_CHAT_ID = telegram_id

DATABASE_URL = "./databases/healthcare.db"


def send_telegram_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            st.error(
                f"Failed to send message: {response.json().get('description', 'Unknown error')}"
            )
            return False
        return True
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False


def get_upcoming_appointments(days_before):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        target_date = (datetime.now() + timedelta(days=days_before)).strftime(
            "%Y-%m-%d"
        )

        query = """
            SELECT User.first_name, User.last_name, User.phone_number, 
                   Appointment.treatment_type, Appointment.appointment_date, Appointment.appointment_time, Appointment.appointmentID
            FROM Appointment
            JOIN User ON Appointment.userID = User.userID
            WHERE Appointment.appointment_date = ?
        """
        cursor.execute(query, (target_date,))
        data = cursor.fetchall()

        df = pd.DataFrame(
            data,
            columns=[
                "First Name",
                "Last Name",
                "Phone Number",
                "Treatment Type",
                "Appointment Date",
                "Appointment Time",
                "Appointment ID",
            ],
        )
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return pd.DataFrame()


def send_reminders(appointments_df, reminder_days):
    for _, row in appointments_df.iterrows():
        appointment_date = row["Appointment Date"]
        appointment_time = row["Appointment Time"]

        message = (
            f"Reminder: Dear {row['First Name']} {row['Last Name']}, "
            f"your {row['Treatment Type']} appointment is on {appointment_date} "
            f"at {appointment_time}."
        )

        if not send_telegram_message(TELEGRAM_CHAT_ID, message):
            st.error(
                f"Failed to send reminder to {row['First Name']} {row['Last Name']}."
            )
        else:
            st.success(f"Reminder sent to {row['First Name']} {row['Last Name']}.")


def search_patient_info(patient_name):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
            SELECT User.first_name, User.last_name, diagnosis, treatment_type, treatment_description, 
                   bone_mass_density, progress_note
            FROM Patient_Info
            JOIN User ON Patient_Info.userID = User.userID
            WHERE User.first_name LIKE ? OR User.last_name LIKE ?
        """
        cursor.execute(query, ("%" + patient_name + "%", "%" + patient_name + "%"))
        data = cursor.fetchall()

        if len(data) == 0:
            st.warning(f"No patient found with the name: {patient_name}")

        df = pd.DataFrame(
            data,
            columns=[
                "First Name",
                "Last Name",
                "Diagnosis",
                "Treatment Type",
                "Treatment Description",
                "Bone Mass Density",
                "Progress Note",
            ],
        )
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


def search_medication_info(patient_name):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
            SELECT Medication.medicationID, User.first_name, User.last_name, medication_name, medication_type, 
                   date_medication_prescribed, medication_treatment_used, side_effect
            FROM Medication
            JOIN User ON Medication.userID = User.userID
            WHERE User.first_name LIKE ? OR User.last_name LIKE ?
        """
        cursor.execute(query, ("%" + patient_name + "%", "%" + patient_name + "%"))
        data = cursor.fetchall()

        df = pd.DataFrame(
            data,
            columns=[
                "Medication ID",
                "First Name",
                "Last Name",
                "Medication Name",
                "Medication Type",
                "Date Prescribed",
                "Treatment Used",
                "Side Effect",
            ],
        )
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


def search_appointments(patient_name):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        query = """
            SELECT Appointment.appointmentID, User.first_name, User.last_name, treatment_type, appointment_type, 
                   appointment_date, appointment_time
            FROM Appointment
            JOIN User ON Appointment.userID = User.userID
            WHERE User.last_name LIKE ? OR User.first_name LIKE ?
        """
        cursor.execute(query, ("%" + patient_name + "%", "%" + patient_name + "%"))
        data = cursor.fetchall()

        df = pd.DataFrame(
            data,
            columns=[
                "Appointment ID",
                "First Name",
                "Last Name",
                "Treatment Type",
                "Appointment Type",
                "Appointment Date",
                "Appointment Time",
            ],
        )
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


def delete_medication(medication_id):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Medication WHERE medicationID = ?", (medication_id,)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Failed to delete medication: {e}")
    except Exception as e:
        st.error(f"Error occurred while deleting medication: {e}")


def delete_appointment(appointment_id):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Appointment WHERE appointmentID = ?", (appointment_id,)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Failed to delete appointment: {e}")
    except Exception as e:
        st.error(f"Error occurred while deleting appointment: {e}")


def update_medication(
    medication_id,
    medication_name,
    medication_type,
    date_prescribed,
    treatment_used,
    side_effect,
):
    try:
        if medication_name.strip() == "" or medication_type.strip() == "":
            st.error("Medication name and type cannot be empty.")
            return

        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Medication
            SET medication_name = ?, medication_type = ?, date_medication_prescribed = ?, 
                medication_treatment_used = ?, side_effect = ?
            WHERE medicationID = ?
        """,
            (
                medication_name,
                medication_type,
                date_prescribed,
                treatment_used,
                side_effect,
                medication_id,
            ),
        )

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Failed to update medication: {e}")
    except Exception as e:
        st.error(f"Error occurred while updating medication: {e}")


def update_appointment(
    appointment_id, appointment_date, appointment_time, treatment_type, appointment_type
):
    try:
        if treatment_type.strip() == "" or appointment_type.strip() == "":
            st.error("Treatment type and appointment type cannot be empty.")
            return

        # Convert date and time to the correct formats
        appointment_date_str = appointment_date.strftime(
            "%Y-%m-%d"
        )  # Convert date to YYYY-MM-DD format
        appointment_time_str = appointment_time.strftime(
            "%H:%M:%S"
        )  # Convert time to HH:MM:SS format

        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Appointment
            SET appointment_date = ?, appointment_time = ?, treatment_type = ?, appointment_type = ?
            WHERE appointmentID = ?
        """,
            (
                appointment_date_str,
                appointment_time_str,
                treatment_type,
                appointment_type,
                appointment_id,
            ),
        )

        conn.commit()
        conn.close()
        st.success(f"Appointment {appointment_id} updated successfully!")
    except sqlite3.Error as e:
        st.error(f"Failed to update appointment: {e}")
    except Exception as e:
        st.error(f"Error occurred while updating appointment: {e}")


def fetch_patient_data():
    # Fetch data from the database
    conn = sqlite3.connect(DATABASE_URL)
    query = """
    SELECT Patient_Info.patientID,Patient_Info.age, Patient_Info.diagnosis, Patient_Info.treatment_type, 
           Medication.medication_name, Medication.medication_type, Patient_Info.bone_mass_density
    FROM Patient_Info 
    LEFT JOIN Medication ON Patient_Info.userID = Medication.userID
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Subheader color
st.markdown(
    """
    <style>
    .custom-subheader {
        font-size:24px;
        color: #4A90E2; /* Soft Blue */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def professional_dashboard():
    try:
        user_role = st.session_state.get("user_role")
        user_id = st.session_state.get("user_id")

        if user_role in ["Admin", "Doctor/Nurse"]:
            st.markdown(
                """
                <style>
                .block-container {
                    padding-left: 1rem; 
                    padding-right: 1rem; 
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "<h1 style='font-size:24px;'>Doctor/Nurse's Dashboard</h1>",
                unsafe_allow_html=True,
            )

            choice = st.sidebar.radio(
                "Select Information Type:",
                ("Overview", "Patient Info", "Medication", "Appointments"),
                index=0,
            )

            if choice == "Overview":
                st.subheader("Overview of Patient Records")
                st.write("This view provides a summary of key metrics.")

                patient_df = fetch_patient_data()

                total_patients = patient_df["patientID"].nunique()
                st.markdown(
                    f"""
                    <div style="background-color:#fafafa; padding:20px; border-radius:10px; text-align:center; border: 1px solid #e1e1e1;">
                        <h2 style="color:#333; font-size: 32px; font-weight: bold; margin: 0;">Total Patients Being Treated</h2>
                        <h1 style="color:#4CAF50; font-size: 50px; font-weight: bold; margin: 10px 0;">{total_patients}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.subheader("Age Distribution of Patients")
                age_histogram = px.histogram(
                    patient_df,
                    x="age",
                    nbins=20,
                    title="Age Distribution",
                    labels={"age": "Age"},
                    height=400,
                )
                st.plotly_chart(age_histogram, use_container_width=True)

                st.subheader("Patients by Treatment Type")
                treatment_count = (
                    patient_df["treatment_type"].value_counts().reset_index()
                )
                treatment_count.columns = ["Treatment Type", "Count"]
                treatment_chart = px.bar(
                    treatment_count,
                    x="Treatment Type",
                    y="Count",
                    color="Treatment Type",
                    title="Number of Patients by Treatment Type",
                    height=400,
                )
                st.plotly_chart(treatment_chart, use_container_width=True)

                st.subheader("Patients by Diagnosis")
                diagnosis_count = patient_df["diagnosis"].value_counts().reset_index()
                diagnosis_count.columns = ["Diagnosis", "Count"]
                diagnosis_chart = px.bar(
                    diagnosis_count,
                    x="Diagnosis",
                    y="Count",
                    color="Diagnosis",
                    title="Number of Patients by Diagnosis",
                    height=400,
                )
                st.plotly_chart(diagnosis_chart, use_container_width=True)

            elif choice == "Patient Info":
                search_query = st.sidebar.text_input("Search by patient name")
                if search_query:
                    df = search_patient_info(search_query)
                    st.subheader("Patient Information")
                    st.dataframe(df)

            elif choice == "Medication":
                search_query = st.sidebar.text_input("Search by patient name")
                if search_query:
                    df = search_medication_info(search_query)
                    st.subheader("Medication Details")
                    if not df.empty:
                        st.dataframe(df)
                        medication_id = st.selectbox(
                            "Select Medication ID to Update",
                            df["Medication ID"].unique(),
                        )
                        selected_row = df[df["Medication ID"] == medication_id].iloc[0]
                        medication_name = st.text_input(
                            "Medication Name", value=selected_row["Medication Name"]
                        )
                        medication_type = st.text_input(
                            "Medication Type", value=selected_row["Medication Type"]
                        )
                        date_prescribed = st.date_input(
                            "Date Prescribed",
                            value=pd.to_datetime(selected_row["Date Prescribed"]),
                        )
                        treatment_used = st.text_input(
                            "Treatment Used", value=selected_row["Treatment Used"]
                        )
                        side_effect = st.text_input(
                            "Side Effect", value=selected_row["Side Effect"]
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Update Medication"):
                                update_medication(
                                    medication_id,
                                    medication_name,
                                    medication_type,
                                    date_prescribed,
                                    treatment_used,
                                    side_effect,
                                )
                                st.success(
                                    f"Medication {medication_id} updated successfully!"
                                )
                        with col2:
                            if st.button("Delete Medication"):
                                delete_medication(medication_id)
                                st.success(
                                    f"Medication {medication_id} deleted successfully!"
                                )

            elif choice == "Appointments":
                search_query = st.sidebar.text_input("Search by patient name")
                if search_query:
                    df = search_appointments(search_query)
                    st.subheader("Appointments Details")
                    if not df.empty:
                        st.dataframe(df)
                        appointment_id = st.selectbox(
                            "Select Appointment ID to Update",
                            df["Appointment ID"].unique(),
                        )
                        selected_row = df[df["Appointment ID"] == appointment_id].iloc[
                            0
                        ]
                        appointment_date = st.date_input(
                            "Appointment Date",
                            value=pd.to_datetime(selected_row["Appointment Date"]),
                        )
                        appointment_time = st.time_input(
                            "Appointment Time",
                            value=pd.to_datetime(
                                selected_row["Appointment Time"]
                            ).time(),
                        )
                        treatment_type = st.text_input(
                            "Treatment Type", value=selected_row["Treatment Type"]
                        )
                        appointment_type = st.text_input(
                            "Appointment Type", value=selected_row["Appointment Type"]
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Update Appointment"):
                                update_appointment(
                                    appointment_id,
                                    appointment_date,
                                    appointment_time,
                                    treatment_type,
                                    appointment_type,
                                )
                                st.success(
                                    f"Appointment {appointment_id} updated successfully!"
                                )
                        with col2:
                            if st.button("Delete Appointment"):
                                delete_appointment(appointment_id)
                                st.success(
                                    f"Appointment {appointment_id} deleted successfully!"
                                )

            # Send reminder for upcoming appointments (1 or 3 days)
            reminder_days = st.sidebar.radio(
                "Send reminder for upcoming appointments in:", (3, 1)
            )
            if st.sidebar.button(
                f"Send Reminder for Appointments in {reminder_days} Day(s)"
            ):
                appointments_df = get_upcoming_appointments(reminder_days)
                if not appointments_df.empty:
                    st.write(
                        f"Sending reminders for appointments in the next {reminder_days} day(s):"
                    )
                    st.table(appointments_df)
                    send_reminders(appointments_df, reminder_days)
                else:
                    st.warning("No appointments in the next days to send reminders.")

        elif user_role == "Patient":
            st.markdown(
                "<h1 style='font-size:24px;'>Welcome to Your Health Dashboard</h1>",
                unsafe_allow_html=True,
            )
            st.write(
                "Here you can see your current medications and upcoming appointments and health tips."
            )
            if user_id:
                conn = sqlite3.connect(DATABASE_URL)
                query_medication = """
                SELECT medication_name, medication_type, date_medication_prescribed, side_effect
                FROM Medication
                WHERE userID = ?
                """
                medication_df = pd.read_sql_query(
                    query_medication, conn, params=(user_id,)
                )
                query_appointments = """
                SELECT appointment_date, appointment_time, treatment_type, appointment_type
                FROM Appointment
                WHERE userID = ?
                ORDER BY appointment_date ASC
                LIMIT 5
                """
                appointments_df = pd.read_sql_query(
                    query_appointments, conn, params=(user_id,)
                )
                conn.close()

                if not medication_df.empty:
                    st.markdown(
                        "<h2 class='custom-subheader'>Your Medications</h2>",
                        unsafe_allow_html=True,
                    )
                    st.dataframe(medication_df)
                if not appointments_df.empty:
                    st.markdown(
                        "<h2 class='custom-subheader'>Your Upcoming Appointments</h2>",
                        unsafe_allow_html=True,
                    )
                    st.dataframe(appointments_df)

                st.subheader("Health Tips")
                st.write(
                    """
                - Stay hydrated and eat a balanced diet.
                - Exercise regularly and maintain a healthy weight.
                - Follow your doctor's advice and take medications as prescribed.
                - Schedule regular follow-ups and screenings.
                """
                )

            else:
                st.warning("Unable to fetch your information. Please contact support.")

        # Telegram and WhatsApp icons URLs
        telegram_icon = (
            "https://upload.wikimedia.org/wikipedia/commons/8/83/Telegram_2019_Logo.svg"
        )
        whatsapp_icon = (
            "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"
        )
        mic_icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Microphone_font_awesome.svg/1200px-Microphone_font_awesome.svg.png"

        st.sidebar.markdown(
            "<h3 style='color: ##000080;'>Contact Us</h3>", unsafe_allow_html=True
        )

        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            telegram_clicked = st.button("Telegram", key="telegram")
        with col2:
            whatsapp_clicked = st.button("WhatsApp", key="whatsapp")

        # Define state for pop-up display
        if "show_popup" not in st.session_state:
            st.session_state["show_popup"] = False

        if "microphone_clicked" not in st.session_state:
            st.session_state["microphone_clicked"] = False

        if telegram_clicked or whatsapp_clicked:
            st.session_state["show_popup"] = True

        # Dark mode styling for the pop-up
        if st.session_state["show_popup"]:
            st.sidebar.markdown(
                f"""
                <div style="background-color: #333333; border-radius: 10px; padding: 20px; color: #FFFFFF; box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
                    <h4 style="color: #FFFFFF;">Work In Progress</h4>
                    <p>- Voice-to-Text and Text-to-Voice functions are currently in progress.</p>
                    <p>- Translation of text and voice to other languages is also under development.</p>
                    <p>Click the microphone icon below to record a message (this feature is not yet functional).</p>
                    <img src="{mic_icon}" alt="Microphone" style="width:40px;margin-top:10px;" />
                </div>
                """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# if __name__ == "__main__":
#    professional_dashboard()
