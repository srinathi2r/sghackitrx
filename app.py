import streamlit as st
from src.registration import user_registration
from src.dashboard import professional_dashboard
from src.image import ocr_page
from src.wound_care import wound_care_analysis
import sqlite3
from PIL import Image
import base64
import os
from openai import OpenAI
from difflib import get_close_matches


# Function to encode the image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Encode the image to base64
image_path = "MISSY Bot.png"  # Adjust this path if the image is in a different location
base64_image = get_base64_image(image_path)

# Custom CSS styles for the title and markdown
st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-family:'Arial', sans-serif;
        color: #ff6347;
    }
    .medium-font {
        font-size:30px !important;
        font-family:'Georgia', serif;
        color: #8B0000;
    }
    </style>
    """, unsafe_allow_html=True)


# Customizing the background image with base64 encoding
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to get OpenAI API key
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "OpenAI API key not found in environment variables. Please set the API key."
        )
    return api_key


# Dictionary to store predefined complaints and responses
complaints_dict = {
    "Is this a chemo drug? My hair has fallen quite a bit recently.": "No, Tamoxifen and Letrozole are not chemo drugs. Hair loss or hair thinning is a common side effect of these medications.",
    "My finger joints hurt when I wake up every morning. Is this normal?": "Yes, joint stiffness and joint pain are common side effects of Letrozole. If the pain is severe, consult your oncologist.",
    "Can we take TCM if we're on tamoxifen?": "Please check with your oncologist before taking any TCMs, as they may interfere with Tamoxifen.",
    "I forgotten to ask the clinic if I'm able to take my thyroid and tamoxifen... Wld u be able to advise?": "Yes, you can continue to take your thyroid medication and rest of the medications together with Tamoxifen.",
    "Can we take TCM if we're on tamoxifen?": "Please always check with your oncologists if you plan to take any TCMs. The reason is to avoid inference with Tamoxifen",
    "For those of us taking Tamoxifen, is it true that we cannot consume grapefruit, tangerine n tumeric? What else should we avoid?": "Grapefruit and tangerine should generally be avoided or consumed with caution while taking tamoxifen. Grapefruit and certain other citrus fruits (like Seville oranges) can interfere with how the liver metabolizes tamoxifen, potentially affecting its effectiveness.",
    "I am experiencing tingling & numbness in my fingers & toes after the chemo. And the numbess is still there even after taking neurobion. Can I ask if any of you have experienced this?": "Yes, patients can still experience of numbness even though they are on neurobion. Neurobion may help to reduce symptoms of neuropath, but they are unlikely to reverse nerve damage entirely. Please inform your breast care nurse to coordinate an appointment for you to see the breast Dr earlier.",
    "I'm just wondering if anyone has experienced blood spotting on tamoxifen and wanna know on their follow up.": "Please inform your breast care nurse to coordinate an appointment for you to see the breast Dr earlier.",
    "i wake up at night feeling warm but not sweaty and hate it as it interrupts my sleep ☹️ what time so u usually take tamoxifen?": "You can try to take tamoxifen in the morning.",
    "Anyone knows the best time to take tamoxifen? I take it in the morning and thinking if it will get better to take it at night?": "There is no strict rule about the best time of day to take Tamoxifen. However, some patients find it helpful to take the medication at a specific time depending on how they manage side effects.Morning: Some people prefer to take it in the morning to avoid potential insomnia or night sweats that might disturb sleep. Night: Others take it in the evening or before bed, especially if they experience nausea or hot flashes, so they can sleep through some of the side effects.",
    "Hi Ladies, just want to ask for those who are taking Tamoxifen. Does it affect your sleep and do u get body or bone pain? what other side effects do you have? ": "The other side effects from Tamoxifen include menopause-like symptoms including hot flashes, night sweats and vaginal dryness. The more serious side effects include blood clots, stroke, and endometrial cancer. However the side effects depends on individual and vary from patient to patient.",
    "if you have time can tell me the results of the blood test.": "Please call the Breast Care Nurse at 6936 5307 during office hours to obtain the results.",
    "got to ask for a memo or hospital visit today": "Please call Breast Centre at 6936 5307 during office hours for the memo.",
    "not so good cos i feel pain sometimes at the chest area. But no more breast there so not sure. i want to change my appointment to earlier than Oct. maybe like 0Ct 22 and i want to take a blood test.": "I can help you. Do you have any drug allergy? If no drug allergy, please take 2 tabs of Panadol, three times a day for pain relief. Call your Breast Care Nurse in the next working day, she can help you with the appointment and concern.",
    "I’m very sad these few days. I just cry n cry for I’m not sure why?": "I cannot imagine what you are going through, but I am here for you. Would you like to talk about what is on your mind?",
    "i am depressed": "I cannot imagine what you are going through, but I am here for you. Have you seen a Dr for your fall?",
    "i will not go clinic today. Got high fever, cough, cold n sore throat. Also very giddy": "I suggest you see your Family Dr/GP for a consultation now.  I will reschedule your appointment with the Breast Dr, your new appointment will be sent to you via SMS.",
    "can help me book for tomorrow at 11.30 for dressing. Thanks": "This is a short notice to reschedule your appointment for tomorrow. Please call Breast Centre at 6936 5307 during office hours.",
    "My dressing side fell off. Should I just wait for Monday": "Do you still have the gauze and plaster which we gave you upon discharge? If yes, please refer to the brochure and reinforce the dressing. If no, please proceed to ward 35 from 10am to 8pm for dressing.",
    "A little better..I try to sleep off the pain": "Aww.. I hope your pain will be better tomorrow. Let me know tomorrow if your pain has worsened.",
    "I am here now for the dressing. Still bleeding": "Please approach room 4 nurses on your bleeding now.",
}


# Function to interact with OpenAI API or predefined responses
def ask_missy(prompt):
    try:
        # Convert the user query to lowercase
        lower_prompt = prompt.lower()

        # Check for exact or partial matches with predefined complaints
        for complaint in complaints_dict:
            # Convert complaint to lowercase for case insensitive comparison
            lower_complaint = complaint.lower()

            # Check if the user's query contains part of a predefined complaint or vice versa
            if lower_complaint in lower_prompt or lower_prompt in lower_complaint:
                return complaints_dict[complaint]

        # Fuzzy matching: Check if there's a close match using difflib
        close_matches = get_close_matches(
            lower_prompt,
            [complaint.lower() for complaint in complaints_dict.keys()],
            n=1,
            cutoff=0.6,
        )
        if close_matches:
            # Return the response for the closest match found
            closest_complaint = next(
                (
                    complaint
                    for complaint in complaints_dict
                    if complaint.lower() == close_matches[0]
                ),
                None,
            )
            if closest_complaint:
                return complaints_dict[closest_complaint]

        # If no predefined complaint matches, use OpenAI API
        api_key = get_api_key()
        if not api_key:
            return "No API key available."

        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful medical assistant capable of answering a wide range of medical and health-related questions. Keep your answers brief and supportive, focusing on providing clear and accurate information.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content
    except Exception as e:
        st.write(f"Error during OpenAI API call: {str(e)}")  # Debug message
        return f"An error occurred: {str(e)}"


if "page" not in st.session_state:
    st.session_state.page = "home"  # Default at home page

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

if "missy_response" not in st.session_state:
    st.session_state.missy_response = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None


def check_user_credentials(username, password):
    conn = sqlite3.connect("./databases/healthcare.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT userID, register_type FROM User WHERE username = ? AND password = ?",
        (username, password),
    )
    user_data = cursor.fetchone()
    conn.close()
    return user_data if user_data else None


def set_page(page):
    st.session_state.page = page


def logout():
    st.session_state.logged_in = False
    st.session_state.page = "home"
    st.session_state.user_role = None
    st.session_state.user_id = None  # Clear the user_id on logout


def show_logout_button():
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Logout"):
            logout()


def show_ask_missy_button():
    if st.session_state.user_role == "Patient":
        col1, col2 = st.columns([8, 2])
        with col2:
            st.markdown("## Need Help?")
            if st.button("Ask MISSY", key="ask_missy"):
                st.session_state.show_missy_form = True


def main():

    if "show_missy_form" not in st.session_state:
        st.session_state.show_missy_form = False

    if "current_navigation" not in st.session_state:
        st.session_state.current_navigation = ""

    st.sidebar.title("Accessibility Settings")
    high_contrast = st.sidebar.checkbox("High Contrast Mode")
    font_size = st.sidebar.slider("Font Size", 12, 32, 16)

    if high_contrast:
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #000;
                color: #FFF;
            }
            .stButton>button {
                background-color: #FFF;
                color: #000;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <style>
        .stApp * {{
            font-size: {font_size}px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    page = st.session_state.page

    if not st.session_state.logged_in:
        if page == "home":
            # Using the custom styles in your Streamlit app
            st.markdown('<p class="big-font">MISSY BOT</p>', unsafe_allow_html=True)
            st.markdown('<p class="medium-font">Your Personalised AI Breast Care Nurse</p>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                option = st.radio(
                    "Choose an option", ["Login", "Register"], horizontal=True
                )
            st.text("Please select 'Login' or 'Register' from the options to continue.")

            if option == "Login":
                st.subheader("Login Page")
                username = st.text_input("Username", label_visibility="hidden")
                password = st.text_input(
                    "Password", type="password", label_visibility="hidden"
                )

                col_login, col_singpass = st.columns([1, 1])
                with col_login:
                    if st.button("Login"):
                        user_data = check_user_credentials(username, password)
                        if user_data:
                            user_id, user_role = user_data
                            st.success(f"Logged in as {user_role}")
                            st.session_state.logged_in = True
                            st.session_state.user_role = user_role
                            st.session_state.user_id = (
                                user_id  # Store user_id in session
                            )
                            if user_role == "Doctor/Nurse":
                                set_page("professional")
                            elif user_role == "Patient":
                                set_page("ocr_only")
                            elif user_role == "Admin":
                                set_page("admin")
                        else:
                            st.error("Invalid username or password.")
                with col_singpass:
                    if st.button("Login with Singpass", key="singpass"):
                        st.success("Login with Singpass is currently not implemented.")

            elif option == "Register":
                user_registration()

    if st.session_state.logged_in:
        # Show logout and "Ask MISSY" buttons at the top
        show_logout_button()
        show_ask_missy_button()

        if st.session_state.user_role == "Doctor/Nurse":
            option = st.sidebar.radio(
                "Navigation", ["Dashboard", "Medication Image Analysis"]
            )
            if option == "Dashboard":
                professional_dashboard()
            elif option == "Medication Image Analysis":
                ocr_page()

        elif st.session_state.user_role == "Patient":
            option = st.sidebar.radio(
                "Navigation",
                ["Dashboard", "Medication Image Analysis", "Wound Care Analysis"],
            )
            if option == "Dashboard":
                professional_dashboard()
            elif option == "Medication Image Analysis":
                ocr_page()
            elif option == "Wound Care Analysis":
                wound_care_analysis()

            # Show "Ask MISSY" form if the button was clicked
            if st.session_state.show_missy_form:
                with st.form(key="missy_form"):
                    # Store user input in session state
                    st.session_state.user_query = st.text_input(
                        "Enter your medical query or health concern:",
                        label_visibility="hidden",
                    )
                    col_submit, col_clear, col_close = st.columns([1, 1, 1])
                    with col_submit:
                        submit_query = st.form_submit_button(label="Submit Query")
                    with col_clear:
                        clear_response = st.form_submit_button(label="Clear Response")
                    with col_close:
                        close_form = st.form_submit_button(label="Close ChatBot")

                    if submit_query and st.session_state.user_query:
                        # Get response from OpenAI API
                        st.session_state.missy_response = ask_missy(
                            f"Patient query: {st.session_state.user_query}"
                        )
                        st.session_state.user_query = (
                            ""  # Clear the input after submission
                        )

                    # Clear response when "Clear Response" button is clicked
                    if clear_response:
                        st.session_state.missy_response = ""
                        st.session_state.user_query = ""

                    # Close the "Ask MISSY" form when "Close Form" button is clicked
                    if close_form:
                        st.session_state.missy_response = ""
                        st.session_state.user_query = ""
                        st.session_state.show_missy_form = False

            # Display response if available
            if st.session_state.missy_response:
                st.markdown("### MISSY's Response")
                st.write(st.session_state.missy_response)

        elif st.session_state.user_role == "Admin":
            option = st.sidebar.radio("Navigation", ["Dashboard", "OCR Image Analysis"])
            if option == "Dashboard":
                professional_dashboard()
            elif option == "OCR Image Analysis":
                ocr_page()


if __name__ == "__main__":
    main()
