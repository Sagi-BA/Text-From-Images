import os

def save_uploaded_file(uploaded_file):
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return temp_file_path
