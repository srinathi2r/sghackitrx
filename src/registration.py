import streamlit as st
import sqlite3


# insert data into database
def insert_user(
    first_name, last_name, username, email, phone_number, password, register_type
):
    conn = sqlite3.connect("./databases/healthcare.db")  # Ensure correct path
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO User (first_name, last_name, username, email, phone_number, password, register_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            first_name,
            last_name,
            username,
            email,
            phone_number,
            password,
            register_type,
        ),
    )

    conn.commit()
    conn.close()


# Registration form function
def user_registration():
    st.title("User Registration")

    # Example custom HTML for accessible registration form
    st.markdown(
        """
        <div aria-label="Registration Form">
            <label for="first_name">First Name:</label>
            <input type="text" id="first_name" name="first_name" placeholder="Enter your first name">
            <br><br>
            <label for="last_name">Last Name:</label>
            <input type="text" id="last_name" name="last_name" placeholder="Enter your last name">
            <br><br>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username">
            <br><br>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" placeholder="Enter your email">
            <br><br>
            <label for="phone_number">Phone Number:</label>
            <input type="tel" id="phone_number" name="phone_number" placeholder="Enter your phone number">
            <br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password">
            <br><br>
            <label for="register_type">Register as:</label>
            <select id="register_type" name="register_type">
                <option value="Doctor/Nurse">Doctor/Nurse</option>
                <option value="Patient">Patient</option>
                <option value="Admin">Admin</option>
            </select>
            <br><br>
            <button onclick="registerUser()">Register</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.text("Already have an account? Go to Login page from the sidebar.")


# You can now call the user_registration function as needed
