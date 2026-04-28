# OCR Text Extractor

A Python-based OCR service with neobrutalist web interface.

## Features
- Image upload via REST API
- Automatic OCR using PaddleOCR/EasyOCR
- SQLite database for queue management
- Neobrutalist UI with smooth animations
- Real-time status updates

## Usage
Access the web interface at the Space URL above.

## API Endpoints
- POST `/api/upload` - Upload image file
- GET `/api/files` - Get all files
- GET `/api/files/<id>` - Get specific file

## Supported Formats
PNG, JPG, JPEG, BMP, TIFF, WEBP, GIF, PDF