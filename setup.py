# setup.py
import os
from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()

BASE_DEPS = [
    'torch',
    'numpy',
    'opencv-python-headless',
    'python-dotenv',
    'psutil',
    'pdf2image',
]

extras_require = {
    'paddleocr': [
        'paddlepaddle>=2.6.2,<3',
        'paddleocr>=2.7.0,<2.8',
        'numpy<1.24',
        'opencv-python-headless<=4.8.1',
    ],
    'easyocr': [
        'easyocr',
        'Pillow',
    ],
}

all_deps = []
for deps in extras_require.values():
    all_deps.extend(deps)
extras_require['all'] = list(set(all_deps))

setup(
    name="ocr-runner",
    version="1.0.0",
    author="Jebin Einstein",
    author_email="jebin@gmail.com",
    description="A flexible, multi-engine OCR runner",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/jebin2/OCR",

    packages=find_packages(),

    install_requires=BASE_DEPS,

    extras_require=extras_require,

    entry_points={
        'console_scripts': [
            'ocr-process=ocr.runner:main',
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.10',
)