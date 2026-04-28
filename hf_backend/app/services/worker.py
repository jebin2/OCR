import asyncio
import os
import json
import shlex
import re
from app.core.config import settings
from custom_logger import logger_config as logger
from app.db import crud

worker_task = None
worker_running = False

def is_worker_running():
    return worker_running

async def start_worker():
    global worker_task, worker_running
    
    logger.info(f"start_worker called: worker_running={worker_running}")
    
    if not worker_running:
        worker_running = True
        worker_task = asyncio.create_task(worker_loop())
        logger.info("Worker task started")
    else:
        logger.info("Worker already running")

async def worker_loop():
    global worker_running
    logger.info("OCR Worker started. Monitoring for new image files...")
    
    while worker_running:
        logger.debug("Worker loop iteration, checking for files...")
        await crud.cleanup_old_entries()
        
        try:
            row = await crud.get_next_not_started()
            
            if row:
                file_id = row['id']
                filepath = row['filepath']
                filename = row['filename']
                
                logger.info(f"\n{'='*60}\nProcessing: {filename}\nID: {file_id}\n{'='*60}")
                
                await crud.update_status(file_id, 'processing')
                
                try:
                    await crud.update_progress(file_id, 10, "Starting OCR...")
                    
                    command = f"cd {settings.CWD} && {settings.PYTHON_PATH} --input {shlex.quote(os.path.abspath(filepath))} --model {settings.OCR_MODEL_NAME}"
                    
                    logger.debug(f"Executing command: {command}")
                    
                    process = await asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT,
                        cwd=settings.CWD,
                        env={
                            **os.environ,
                            'PYTHONUNBUFFERED': '1',
                            'CUDA_LAUNCH_BLOCKING': '1',
                            'USE_CPU_IF_POSSIBLE': 'true'
                        }
                    )
                    
                    while True:
                        line = await process.stdout.readline()
                        if not line:
                            break
                            
                        line_str = line.decode('utf-8', errors='replace').strip()
                        if line_str:
                            logger.info(f"[OCR] {line_str}")
                            
                            percent_match = re.search(r'(\d+)%', line_str)
                            if percent_match:
                                try:
                                    percent = int(percent_match.group(1))
                                    await crud.update_progress(file_id, min(percent, 90), "Processing...")
                                except: pass
                            
                            if 'loading model' in line_str.lower() or 'initializing' in line_str.lower():
                                await crud.update_progress(file_id, 20, "Loading model...")
                            elif 'processing' in line_str.lower():
                                await crud.update_progress(file_id, 50, "Processing image...")
                    
                    await process.wait()
                    if process.returncode != 0:
                        raise Exception(f"OCR process failed with return code {process.returncode}")
                    
                    await crud.update_progress(file_id, 95, "Reading results...")
                    
                    output_path = os.path.join(settings.CWD, settings.TEMP_DIR, 'output_ocr.json')
                    with open(output_path, 'r') as file:
                        result = json.loads(file.read().strip())
                    
                    ocr_text = result.get('text', '') or str(result)
                    
                    logger.success(f"Successfully processed: {filename}")
                    logger.info(f"Text preview: {ocr_text[:100]}...")
                    
                    await crud.update_status(file_id, 'completed', ocr_text=json.dumps(result))
                    
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.debug(f"Deleted image file: {filepath}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {str(e)}")
                    await crud.update_status(file_id, 'failed', error=str(e))
                    
            else:
                await asyncio.sleep(settings.POLL_INTERVAL)
                
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            await asyncio.sleep(settings.POLL_INTERVAL)
