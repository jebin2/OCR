import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
logging.getLogger().setLevel(logging.ERROR)

from pathlib import Path
import os
import json
import gc
import cv2

from dotenv import load_dotenv
if os.path.exists(".env"):
    print("Loaded load_dotenv")
    load_dotenv()

class BaseOCR:
    """Base class for OCR implementations"""
    
    def __init__(self, type):
        from . import common
        self.device = common.get_device()
        self.type = type
        self.input_file = None
        self.temp_dir = "./temp_dir"
        self.output_text_file = f"{self.temp_dir}/output_ocr.txt"
        self.output_json_file = f"{self.temp_dir}/output_ocr.json"
        self.output_visual_file = f"{self.temp_dir}/output_ocr_visual.txt"
        self.model = None
        self.default_language = 'en'
        self.compact_mode = False

    def reset(self):
        if self.device == "cuda":
            import torch
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

    def validate_input_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return True
    
    def _is_image_file(self, file_path: str) -> bool:
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp', '.gif')
        return file_path.lower().endswith(image_extensions)

    def _is_pdf_file(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')

    def _convert_pdf_to_images(self, pdf_path: str) -> list:
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image is required for PDF processing. Install it with: pip install pdf2image")

        images = convert_from_path(pdf_path)
        image_paths = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(self.temp_dir, f"page_{i+1}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
        
        print(f"Converted PDF to {len(image_paths)} images")
        return image_paths

    def save_ocr_results(self, result):
        """Save OCR results to files."""
        visual_output = self._generate_visual_output(result)
        
        with open(self.output_text_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        print(f"Text OCR saved as {self.output_text_file}")
        
        with open(self.output_json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"JSON OCR saved as {self.output_json_file}")
        
        with open(self.output_visual_file, 'w', encoding='utf-8') as f:
            f.write(visual_output)
        print(f"Visual OCR saved as {self.output_visual_file}")
        
        return True

    def _generate_visual_output(self, result):
        """Generate text-based layout reconstruction of OCR results."""
        if "results" not in result or not result["results"]:
            return result.get("text", "")
        
        detections = []
        for item in result.get("results", []):
            text = item.get("text", "")
            box = item.get("box", [])
            
            if text and box and len(box) >= 4:
                x_coords = [p[0] for p in box]
                y_coords = [p[1] for p in box]
                
                detections.append({
                    'text': text,
                    'min_x': min(x_coords),
                    'max_x': max(x_coords),
                    'min_y': min(y_coords),
                    'max_y': max(y_coords),
                })
        
        if not detections:
            return result.get("text", "")
        
        global_min_x = min(d['min_x'] for d in detections)
        global_max_x = max(d['max_x'] for d in detections)
        global_min_y = min(d['min_y'] for d in detections)
        global_max_y = max(d['max_y'] for d in detections)
        
        content_w = global_max_x - global_min_x
        content_h = global_max_y - global_min_y
        
        if content_w == 0 or content_h == 0:
            return result.get("text", "")
        
        output_width = 120
        output_height = int(output_width * (content_h / content_w) * 0.5)
        
        grid = [[' ' for _ in range(output_width)] for _ in range(output_height)]
        
        scale_x = output_width / content_w
        scale_y = output_height / content_h
        
        for det in detections:
            grid_x = int((det['min_x'] - global_min_x) * scale_x)
            grid_y = int((det['min_y'] - global_min_y) * scale_y)
            
            grid_x = max(0, min(grid_x, output_width - 1))
            grid_y = max(0, min(grid_y, output_height - 1))
            
            for j, char in enumerate(det['text']):
                if grid_x + j < output_width:
                    grid[grid_y][grid_x + j] = char
        
        if self.compact_mode:
            grid = self._compress_grid(grid)
        
        output_lines = []
        for row in grid:
            if isinstance(row, list):
                row = "".join(row)
            output_lines.append(row.rstrip() if row.strip() else "")

        return "\n".join(output_lines)
    
    def _compress_grid(self, grid):
        """Compress grid by removing empty rows and columns."""
        grid = [''.join(row) if isinstance(row, list) else row for row in grid]
        
        new_grid = []
        for row in grid:
            if row and any(c != ' ' for c in row):
                new_grid.append(row)
            elif not new_grid or any(c != ' ' for c in new_grid[-1]):
                new_grid.append(row)
        
        if not new_grid:
            return grid
        
        max_len = max(len(row) for row in new_grid)
        padded = [row.ljust(max_len) for row in new_grid]
        
        col_empty = []
        for col_idx in range(max_len):
            if all(row[col_idx] == ' ' for row in padded):
                col_empty.append(col_idx)
        
        result = []
        for row in padded:
            new_row = ''.join(c for idx, c in enumerate(row) if idx not in col_empty)
            result.append(new_row)
        
        return result

    def transcribe(self, args):
        """Main OCR method to be implemented by subclasses."""
        self.reset()
        input_file = args.get('input') if isinstance(args, dict) else getattr(args, 'input', None)

        self.validate_input_file(input_file)

        # Handle PDF files - convert to images first
        if self._is_pdf_file(input_file):
            print(f"Detected PDF file: {input_file}")
            image_files = self._convert_pdf_to_images(input_file)
            
            all_results = []
            for img_file in image_files:
                result = self.generate_ocr(img_file)
                if result:
                    all_results.append(result)
            
            if not all_results:
                return False
            
            # Merge results from all pages
            merged_text = "\n\n".join([r["text"] for r in all_results])
            merged_result = {
                "text": merged_text,
                "language": all_results[0].get("language", ""),
                "model": all_results[0].get("model", ""),
                "pages": len(all_results),
                "engine": self.type,
                "results": all_results
            }
            
            success = self.save_ocr_results(merged_result)
            return merged_result if success else False

        elif self._is_image_file(input_file):
            print(f"Detected image file: {input_file}")
            result = self.generate_ocr(input_file)
            
            if not result:
                print("Error: No OCR generated")
                return False
            
            success = self.save_ocr_results(result)
            return result if success else False
        else:
            raise ValueError("Error: Unsupported file format. Supported formats: .png, .jpg, .jpeg, .bmp, .tiff, .webp, .gif, .pdf")

    def generate_ocr(self, input_file):
        """Generate OCR - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate_ocr method")

    def cleanup(self):
        """Clean up model resources."""
        if hasattr(self, 'model') and self.model is not None:
            print("Cleaning up model...")
            try:
                del self.model
                gc.collect()
                try:
                    if self.device == "cuda":
                        import torch
                        torch.cuda.empty_cache()
                        torch.cuda.ipc_collect()
                except ImportError:
                    pass
                print("Model memory cleaned.")
            except Exception as e:
                print(f"Error during model cleanup: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __del__(self):
        self.cleanup()