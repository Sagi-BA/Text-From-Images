import streamlit as st
import os
import asyncio
from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, decrement_user_count, get_user_count
from utils.ChatWithImageClass import ChatWithImageClass
from utils.tools import save_uploaded_file
from utils.TelegramSender import TelegramSender
from io import BytesIO

# Initialize logging
# logging.basicConfig(level=logging.INFO)
UPLOAD_DIR = "uploads"

# Ensure environment variable is set
if os.getenv("GOOGLE_CLOUD_VISION_API_KEY") is None or os.getenv("GOOGLE_CLOUD_VISION_API_KEY") == "":
    st.error("GOOGLE_CLOUD_VISION_API_KEY is not set. Please set it in the environment variables.")
    st.stop()

# Initialize the model once
if 'google_model' not in st.session_state:
    st.session_state.google_model = ChatWithImageClass()

# Initialize TelegramSender
if 'telegram_sender' not in st.session_state:
    st.session_state.telegram_sender = TelegramSender()

# Increment user count if this is a new session
if 'counted' not in st.session_state:
    st.session_state.counted = True
    increment_user_count()

# Initialize user count
initialize_user_count()

# Register a function to decrement the count when the session ends
def on_session_end():
    decrement_user_count()

st.session_state.on_session_end = on_session_end

def start_over():
    # Keys to keep
    keys_to_keep = ['counted', 'on_session_end', 'google_model', 'telegram_sender']
    
    # Remove all keys except the ones we want to keep
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    # Reset the active_tab
    st.session_state.active_tab = None
    
    print("Session state cleared for Start Over")

def process_image(image, filename):
    file_path = save_uploaded_file(image, UPLOAD_DIR, filename)
    st.image(file_path, caption=f"תמונה שהועלתה", use_column_width=True)        
    
    text_key = f'text_{filename}'
    if text_key not in st.session_state:
        with st.spinner('מחלץ טקסט... אנא המתן.'):
            text = st.session_state.google_model.detect_text_with_googleapi(file_path)
            text = text.strip() if text else "לא נמצא טקסט בתמונה"
            st.session_state[text_key] = text
            
            # Send image and text to Telegram asynchronously
            asyncio.run(st.session_state.telegram_sender.send_image_and_text(file_path, text))
    
    text = st.session_state[text_key]
    text_area_id = f'text_area_{filename}'
    st.text_area(f"טקסט שחולץ", value=text, key=text_area_id, height=200)
    
    st.markdown("---")  # Add a separator between images

def main():
    # Initialize Streamlit configuration and load resources
    header_content, footer_content = initialize()

    # Header
    st.markdown(header_content)

    # Add custom CSS for button styling
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0099ff;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #0099ff;
        border-radius: 10px;
        padding: 10px 24px;
        margin: 10px 0px;
    }
    div.stButton > button:hover {
        background-color: #0077cc;
        border-color: #0077cc;
    }
    </style>""", unsafe_allow_html=True)

    # Handle the "Start Over" button click
    if st.button("התחל מחדש", use_container_width=True):
        start_over()

    # Create two columns for the icon buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📁 העלאת קובץ", key="upload_button", use_container_width=True):
            st.session_state.active_tab = "upload"

    with col2:
        if st.button("📷 צילום מהמצלמה", key="camera_button", use_container_width=True):
            st.session_state.active_tab = "camera"

    # Handle file upload
    if st.session_state.get('active_tab') == "upload":
        uploaded_files = st.file_uploader(
            "העלה תמונות",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg']
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                process_image(uploaded_file, uploaded_file.name)

    # Handle camera capture
    elif st.session_state.get('active_tab') == "camera":
        camera_image = st.camera_input("צלם תמונה")
        
        if camera_image:
            # Convert the camera input to a file-like object
            image_bytes = camera_image.getvalue()
            image_file = BytesIO(image_bytes)
            image_file.name = "camera_capture.jpg"
            
            process_image(image_file, image_file.name)

    user_count = get_user_count(formatted=True)
    footer_with_count = f"{footer_content}\n\n<p class='user-count'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

if __name__ == "__main__":
    main()