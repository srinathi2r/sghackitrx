import streamlit as st
from PIL import Image
import numpy as np
import os

# Image-recommendation mapping
image_recommendations = {
    "image1.png": "Advise to reinforce drain site dressing on her own, using the set of gauze and plaster (given to patient upon discharge) given by the Breast Care Nurses. Return to Breast Centre in the next working day.",
    "image2.png": "Advise to return to Breast Centre for change of dressing during office hours. After office hours, proceed to ward 35 between 10am to 8pm.",
    "image3.png": "Advise to return to Breast Centre for change of dressing during office hours. After office hours, proceed to ward 35 between 10am to 8pm.",
    "image4.png": "Advise to return to Breast Centre for change of dressing during office hours. After office hours, proceed to ward 35 between 10am to 8pm.",
    "image5.png": "Advise to reinforce drain site dressing on her own, using the set of gauze and plaster (given to patient upon discharge) given by the Breast Care Nurses. Return to Breast Centre in the next working day.",
    "image6.png": "Advise to return to Breast Centre for change of drain bottle during office hours.After office hours, proceed to ward 35 between 10am to 8pm.",
    "image7.png": "Reassurance given to patient, drain bottle vacuum intact. Appointment with Breast Care Nurse remain.",
}


# Function to calculate similarity between two images
def image_similarity(image1, image2):
    image1 = image1.resize((128, 128)).convert("L")
    image2 = image2.resize((128, 128)).convert("L")
    array1 = np.array(image1).flatten()
    array2 = np.array(image2).flatten()
    return np.corrcoef(array1, array2)[0, 1]


# Function to display wound care analysis in Streamlit
def wound_care_analysis():
    st.title("Wound Care Recommendation System")

    # Load known images and compute their similarity scores
    image_directory = "./wound care images/"
    known_images = {}
    for image_name in image_recommendations.keys():
        image_path = os.path.join(image_directory, image_name)
        with Image.open(image_path) as img:
            known_images[image_name] = img.copy()  # Copy to avoid file handle issues

    # Streamlit Interface for Upload
    uploaded_image = st.file_uploader(
        "Upload a wound image", type=["jpg", "jpeg", "png"]
    )

    if uploaded_image is not None:
        # Display the uploaded image as a small picture
        uploaded_image = Image.open(uploaded_image)
        st.image(
            uploaded_image, caption="Uploaded Image", width=200
        )  # Adjust width as needed

        # Initialize variables to track the best match
        max_similarity = 0
        best_match = None

        # Compare uploaded image with each known image
        for image_name, known_image in known_images.items():
            similarity = image_similarity(known_image, uploaded_image)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = image_name

        # Display the best match recommendation if similarity is above a threshold
        similarity_threshold = 0.9  # Adjust threshold as needed
        if max_similarity >= similarity_threshold:
            st.success(f"Recommendation: {image_recommendations[best_match]}")
        else:
            st.warning(
                "No high similarity found for this image. Please consult a medical professional."
            )
