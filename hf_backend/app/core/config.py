import os

class Config:
    PORT = int(os.environ.get('PORT', 7860))
    UPLOAD_FOLDER = 'uploads'
    TEMP_DIR = 'temp_dir'
    DATABASE_FILE = 'ocr_results.db'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp', 'gif', 'pdf'}
    
    CWD = "./"
    PYTHON_PATH = "ocr-process"
    OCR_MODEL_NAME = "paddleocr"
    POLL_INTERVAL = 3

settings = Config()

os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
