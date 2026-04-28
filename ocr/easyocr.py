from typing import Optional, Dict, Any, List
from .base import BaseOCR

class EasyOCRProcessor(BaseOCR):
    """OCR processor using EasyOCR."""
    
    def __init__(self, lang_list=['en'], use_gpu=True, model_storage_directory=None):
        super().__init__("easyocr")
        self.lang_list = lang_list
        self.use_gpu = use_gpu and self.device == "cuda"
        self.model_storage_directory = model_storage_directory or "./models/easyocr"
        self._load_model()

    def _load_model(self):
        """Load EasyOCR model."""
        print("Initializing EasyOCR...")
        import easyocr
        
        reader_args = {
            'lang_list': self.lang_list,
            'gpu': self.use_gpu,
            'model_storage_directory': self.model_storage_directory,
            'download_enabled': True,
            'verbose': False
        }
        
        self.model = easyocr.Reader(**reader_args)
        print("EasyOCR model loaded successfully!")

    def generate_ocr(self, input_file):
        """Generate OCR using EasyOCR."""
        print(f"Processing: {input_file}")
        
        result = self.model.readtext(input_file)
        
        if not result:
            print("No text detected in the image")
            return None
        
        all_text = []
        all_results = []
        
        for detection in result:
            box = detection[0]
            text = detection[1]
            confidence = detection[2]
            
            all_text.append(text)
            if box:
                box_list = [[float(p[0]), float(p[1])] for p in box]
            else:
                box_list = []
            all_results.append({
                "text": text,
                "confidence": float(confidence),
                "box": box_list
            })
        
        full_text = " ".join(all_text)
        
        ocr_result = {
            "text": full_text,
            "language": ",".join(self.lang_list),
            "model": f"{self.type}-{self.lang_list}",
            "engine": self.type,
            "results": all_results
        }
        
        print(f"OCR completed successfully! Detected {len(all_results)} text regions")
        return ocr_result