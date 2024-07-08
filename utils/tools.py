import os

# def save_uploaded_file(uploaded_file):
#     temp_dir = 'uploads'
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)
#     temp_file_path = os.path.join(temp_dir, uploaded_file.name)
#     with open(temp_file_path, 'wb') as f:
#         f.write(uploaded_file.getbuffer())
#     return temp_file_path

def save_uploaded_file(uploaded_file, upload_dir="uploads"):
    """
    Save the uploaded file to the specified directory and return the file path.
    """
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
