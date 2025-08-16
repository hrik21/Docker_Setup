import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

def setup_upload_folder():
    """Create upload folder if it doesn't exist"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Upload folder '{UPLOAD_FOLDER}' ready")

def is_allowed_file(filename):
    """Check if file has allowed extension (PDF only)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return filename and file path"""
    if not file or file.filename == '':
        return None, None
    
    if not is_allowed_file(file.filename):
        return None, None
    
    # Make filename safe
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save file to disk
    file.save(file_path)
    print(f"File saved: {file_path}")
    
    return filename, file_path