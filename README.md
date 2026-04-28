# OCR-Runner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)

A flexible, multi-engine command-line tool for Optical Character Recognition (OCR).

This tool provides a unified interface to extract text from images using different OCR engines with visual output support.

### Key Features

- **Multiple Engine Support**: Easily switch between different OCR engines.
  - **PaddleOCR**: Fast and accurate
  - **EasyOCR**: Supports 80+ languages
- **Visual Output**: Generate text layout visualization
- **Compact Mode**: Remove empty rows/columns for cleaner output
- **Flexible Input**: Supports PNG, JPG, PDF, and more

## Installation

```bash
git clone https://github.com/jebin/ocr.git
cd ocr

# Install with pip
pip install -e .

# Install paddleocr dependencies
pip install -r paddleocr_requirements.txt

# Or install easyocr dependencies
pip install -r easyocr_requirements.txt

# For all engines
pip install -r paddleocr_requirements.txt -r easyocr_requirements.txt
```

## Usage

### Basic OCR

```bash
# Using PaddleOCR (default)
ocr-runner --input path/to/image.jpg

# Using EasyOCR
ocr-runner --input path/to/image.jpg --model easyocr
```

### Options

- `--model {paddleocr,easyocr}` - OCR engine (default: paddleocr)
- `--cpu` - Force CPU usage (no GPU)
- `-c, --compact` - Compact visual output (remove empty rows/columns)

### Server Mode

For batch processing:

```bash
ocr-runner --model paddleocr --server-mode
```

## Output Files

For each run, the tool generates the following files in `temp_dir`:

- `output_ocr.txt`: The extracted text
- `output_ocr.json`: JSON with text and bounding boxes
- `output_ocr_visual.txt`: Visual layout representation

## Supported Engines

| Engine | argument `--model` | Notes |
| :--- | :--- |:---|
| PaddleOCR | `paddleocr` | Fast and accurate, Chinese support |
| EasyOCR | `easyocr` | 80+ languages, GPU recommended |