from typing import Optional, Dict, Any, List
from .base import BaseOCR
import logging

class PaddleOCRProcessor(BaseOCR):
    """OCR processor using PaddleOCR."""
    
    def __init__(self, use_angle_cls=True, lang='en'):
        super().__init__("paddleocr")
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self._load_model()

    def _load_model(self):
        """Load PaddleOCR model."""
        print("Initializing PaddleOCR...")
        
        from paddleocr import PaddleOCR
        
        logging.getLogger("ppocr").setLevel(logging.ERROR)
        
        ocr_args = {
            'use_angle_cls': self.use_angle_cls,
            'lang': self.lang,
            'device': 'gpu' if self.device == "cuda" else 'cpu',
        }
        
        self.model = PaddleOCR(**ocr_args)
        print("PaddleOCR model loaded successfully!")

    def generate_ocr(self, input_file):
        """Generate OCR using PaddleOCR."""
        print(f"Processing: {input_file}")
        
        result = self.model.ocr(input_file)
        
        if not result or not result[0]:
            print("No text detected in the image")
            return None
        
        all_text = []
        all_results = []
        
        for line in result[0]:
            if line:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                all_text.append(text)
                box_list = [[float(p[0]), float(p[1])] for p in box]
                all_results.append({
                    "text": text,
                    "confidence": float(confidence),
                    "box": box_list
                })
        
        full_text = " ".join(all_text)
        
        ocr_result = {
            "text": full_text,
            "language": self.lang,
            "model": f"{self.type}-{self.lang}",
            "engine": self.type,
            "results": all_results
        }
        
        print(f"OCR completed successfully! Detected {len(all_results)} text regions")
        return ocr_result