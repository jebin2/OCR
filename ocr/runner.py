import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
logging.getLogger().setLevel(logging.ERROR)

import argparse
import os
import sys
import subprocess

OCR_ENGINE = None

def server_mode(args):
    """Run in server mode - read commands from stdin."""
    global OCR_ENGINE
    
    while True:
        input_line = sys.stdin.readline().strip()
        if not input_line:
            break
        
        args.input = input_line

        result = initiate(args)
        
        if result:
            print(f"SUCCESS: {args.input}")
        else:
            print(f"ERROR: {args.input}")
        sys.stdout.flush()

def check_for_dependency(model):
    requirements_file_name = f"{model}_requirements.txt"

    if not os.path.isfile(requirements_file_name):
        raise FileNotFoundError(f"Requirements file '{requirements_file_name}' not found for model '{model}'.")

    try:
        print(f"Checking dependencies for model: {model}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file_name]
        )
        print(f"Dependencies for '{model}' installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies for '{model}': {e}")
        sys.exit(1)

def current_env():
    """Detect current virtual environment."""
    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path:
        return os.path.basename(venv_path)
    return None

def initiate(args):
    model = args.get('model') if isinstance(args, dict) else getattr(args, 'model', None)
    use_cpu = args.get('cpu') if isinstance(args, dict) else getattr(args, 'cpu', False)
    compact = args.get('compact') if isinstance(args, dict) else getattr(args, 'compact', False)
    
    if use_cpu:
        os.environ["USE_CPU_IF_POSSIBLE"] = "1"
    elif os.environ.get("USE_CPU_IF_POSSIBLE"):
        del os.environ["USE_CPU_IF_POSSIBLE"]
    
    env_name = current_env()
    
    if not model and env_name:
        if env_name == "paddleocr_env":
            model = "paddleocr"
        elif env_name == "easyocr_env":
            model = "easyocr"
    
    if not model:
        raise ValueError("Please specify --model (paddleocr, easyocr) or set env to paddleocr_env/easyocr_env")
    
    if model == "paddleocr":
        from .paddleocr import PaddleOCRProcessor as OCREngine
    elif model == "easyocr":
        from .easyocr import EasyOCRProcessor as OCREngine
    else:
        raise ValueError(f"Unknown model: {model}. Use --model paddleocr or --model easyocr")

    # check_for_dependency(model)

    global OCR_ENGINE
    needs_reload = OCR_ENGINE and (
        (use_cpu and OCR_ENGINE.device == "cuda") or 
        (not use_cpu and OCR_ENGINE.device == "cpu")
    )
    
    if needs_reload:
        OCR_ENGINE.cleanup()
        OCR_ENGINE = None
    
    if not OCR_ENGINE:
        OCR_ENGINE = OCREngine()
    
    OCR_ENGINE.compact_mode = compact

    result = OCR_ENGINE.transcribe(args)
    return result

def main():
    parser = argparse.ArgumentParser(
        description="OCR processor using various OCR engines"
    )
    parser.add_argument(
        "--server-mode", 
        action="store_true", 
        help="Run in server mode (read commands from stdin)"
    )
    parser.add_argument(
        "--input", 
        help="Input image/PDF file path"
    )
    parser.add_argument(
        "--model",
        help="OCR model name (paddleocr, easyocr)"
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU usage"
    )
    parser.add_argument(
        "-c", "--compact",
        action="store_true",
        help="Compact output (text only)"
    )
    
    args = parser.parse_args()

    if args.server_mode:
        server_mode(args)
    else:
        if not args.input:
            print("Error: --input is required when not in server mode")
            return 1

        result = initiate(args)
        return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())