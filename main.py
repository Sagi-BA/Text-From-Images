import streamlit as st
import os
from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, decrement_user_count, get_user_count
from utils.ChatWithImageClass import ChatWithImageClass
from utils.tools import save_uploaded_file
import pyperclip
from streamlit.components.v1 import html

# Initialize logging
# logging.basicConfig(level=logging.INFO)

# Ensure environment variable is set
if os.getenv("GOOGLE_CLOUD_VISION_API_KEY") is None or os.getenv("GOOGLE_CLOUD_VISION_API_KEY") == "":
    st.error("GOOGLE_CLOUD_VISION_API_KEY is not set. Please set it in the environment variables.")
    st.stop()

# Initialize the model once
# if 'google_model' not in st.session_state:
#     st.session_state.google_model = ChatWithImageClass()

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

def clipboard_copy_clicked(text_area_id):
    print(f"clipboard_copy_clicked called with text_area_id: {text_area_id}")
    if text_area_id in st.session_state:
        text = st.session_state[text_area_id]
        pyperclip.copy(text)
        print(f"Text copied to clipboard: {text[:50]}...")  # Log first 50 chars
        st.success("הטקסט הועתק ללוח בהצלחה!", icon="✅")
    else:
        print(f"text_area_id {text_area_id} not found in session_state")
        st.error(f"Error: Could not find text for {text_area_id}")

def start_over():
    # Keys to keep
    keys_to_keep = ['counted', 'on_session_end', 'google_model']
    
    # Remove all keys except the ones we want to keep
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    # Increment the file uploader key to force a reset
    st.session_state['file_uploader_key'] = st.session_state.get('file_uploader_key', 0) + 1
    
    print("Session state cleared for Start Over")

def main():
# Initialize Streamlit configuration and load resources
    header_content, footer_content = initialize()

    # Header
    st.markdown(header_content)

    # Handle the "Start Over" button click
    if st.button("התחל מחדש", use_container_width=True):
        start_over()

    # File uploader
    file_uploader_key = f"file_uploader_{st.session_state.get('file_uploader_key', 0)}"
    uploaded_files = st.file_uploader(
        "העלה תמונות",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg'],
        key=file_uploader_key
    )

    if uploaded_files:
        for i, uploaded_file in enumerate(uploaded_files):
            # Display the uploaded image
            with st.spinner('מחלץ טקסט... אנא המתן.'):
                st.image(uploaded_file, caption=f"תמונה שהועלתה: {uploaded_file.name}", use_column_width=True)        
                
                text = "sss" #st.session_state.google_model.detect_text_with_googleapi(save_uploaded_file(uploaded_file))
                text = text.strip() if text else ""
                text_area_id = f'text_area_{i}'
                st.text_area(f"טקסט שחולץ {i+1}", value=text, key=text_area_id, height=200)
                if st.button('העתק ללוח', key=f'button_{i}'):
                    clipboard_copy_clicked(text_area_id)
                st.markdown("---")  # Add a separator between images

    user_count = get_user_count(formatted=True)
    footer_with_count = f"{footer_content}\n\n<p class='user-count'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
