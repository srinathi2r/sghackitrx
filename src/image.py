import streamlit as st
from PIL import Image, ImageDraw
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import pyttsx3


def perform_ocr(uploaded_file):
    # Load OCR model
    model = ocr_predictor(
        det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True
    )

    # Convert uploaded file to a PIL image
    image = Image.open(uploaded_file)

    # Save PIL image to a temporary file
    temp_image_path = "temp_image.jpg"
    image.save(temp_image_path)

    # Load image using DocumentFile
    single_img_doc = DocumentFile.from_images(temp_image_path)

    result = model(single_img_doc)

    words_list = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    words_list.append(word.value)

    extracted_text = " ".join(words_list)

    return extracted_text, result, image


def draw_boxes(image, result):
    draw = ImageDraw.Draw(image)

    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    bbox = word.geometry  # Get bounding box
                    # Convert normalized coordinates to actual coordinates
                    left, top = bbox[0][0] * image.width, bbox[0][1] * image.height
                    right, bottom = bbox[1][0] * image.width, bbox[1][1] * image.height
                    draw.rectangle([left, top, right, bottom], outline="red", width=2)
    return image


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def ocr_page():
    st.title("Medication Recognition App")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:

        extracted_text, result, image = perform_ocr(uploaded_file)

        image_with_boxes = draw_boxes(image.copy(), result)

        with st.sidebar:
            st.header("Settings")
            text_size = st.slider("Adjust Text Size", 10, 50, 20)
            if st.button("Read Text Aloud"):
                text_to_speech(extracted_text)

        col1, col2 = st.columns(2)

        with col1:

            st.image(
                image_with_boxes,
                caption="OCR Result (with bounding boxes)",
                use_column_width=True,
            )

        with col2:

            st.write("Extracted Text:")
            st.markdown(
                f'<p style="font-size:{text_size}px;">{extracted_text}</p>',
                unsafe_allow_html=True,
            )
