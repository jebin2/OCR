from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import threading
import subprocess
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp', 'gif', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('temp_dir', exist_ok=True)

worker_thread = None
worker_running = False

def init_db():
    conn = sqlite3.connect('ocr_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS image_files
                 (id TEXT PRIMARY KEY,
                  filename TEXT NOT NULL,
                  filepath TEXT NOT NULL,
                  status TEXT NOT NULL,
                  ocr_text TEXT,
                  created_at TEXT NOT NULL,
                  processed_at TEXT,
                  progress INTEGER DEFAULT 0,
                  progress_text TEXT,
                  hide_from_ui INTEGER DEFAULT 0)'''
    )
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def start_worker():
    global worker_thread, worker_running
    
    if not worker_running:
        worker_running = True
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
        print("Worker thread started")

def cleanup_old_entries():
    from datetime import timedelta
    
    try:
        conn = sqlite3.connect('ocr_results.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=10)).isoformat()
        
        c.execute('''SELECT id, filepath FROM image_files 
                     WHERE created_at < ?''', (cutoff_date,))
        old_entries = c.fetchall()
        
        if old_entries:
            deleted_files = 0
            deleted_rows = 0
            
            for entry in old_entries:
                filepath = entry['filepath']
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        deleted_files += 1
                    except Exception as e:
                        print(f"Failed to delete old file {filepath}: {e}")
            
            c.execute('''DELETE FROM image_files WHERE created_at < ?''', (cutoff_date,))
            deleted_rows = c.rowcount
            conn.commit()
            
            if deleted_rows > 0 or deleted_files > 0:
                print(f"Cleanup: Deleted {deleted_rows} old entries and {deleted_files} files (older than 10 days)")
        
        conn.close()
    except Exception as e:
        print(f"Cleanup error: {e}")

def worker_loop():
    print("OCR Worker started. Monitoring for new image files...")
    
    CWD = "./"
    PYTHON_PATH = "ocr-process"
    OCR_MODEL_NAME = "paddleocr"
    POLL_INTERVAL = 3
    
    import shlex
    import json
    
    while worker_running:
        cleanup_old_entries()
        try:
            conn = sqlite3.connect('ocr_results.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('''SELECT * FROM image_files 
                         WHERE status = 'not_started' 
                         ORDER BY created_at ASC 
                         LIMIT 1''')
            row = c.fetchone()
            conn.close()
            
            if row:
                file_id = row['id']
                filepath = row['filepath']
                filename = row['filename']
                
                print(f"\n{'='*60}")
                print(f"Processing: {filename}")
                print(f"ID: {file_id}")
                print(f"{'='*60}")
                
                update_status(file_id, 'processing')
                
                try:
                    update_progress(file_id, 10, "Starting OCR...")
                    
                    command = f"""cd {CWD} && {PYTHON_PATH} --input {shlex.quote(os.path.abspath(filepath))} --model {OCR_MODEL_NAME}"""
                    
                    import re
                    
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        executable="/bin/bash",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        cwd=CWD,
                        text=True,
                        bufsize=1,
                        env={
                            **os.environ,
                            'PYTHONUNBUFFERED': '1',
                            'CUDA_LAUNCH_BLOCKING': '1',
                            'USE_CPU_IF_POSSIBLE': 'true'
                        }
                    )
                    
                    for line in process.stdout:
                        print(line, end='')
                        
                        percent_match = re.search(r'(\d+)%', line)
                        if percent_match:
                            try:
                                percent = int(percent_match.group(1))
                                update_progress(file_id, min(percent, 90), "Processing...")
                            except: pass
                        
                        if 'loading model' in line.lower() or 'initializing' in line.lower():
                            update_progress(file_id, 20, "Loading model...")
                        elif 'processing' in line.lower():
                            update_progress(file_id, 50, "Processing image...")
                    
                    process.wait()
                    if process.returncode != 0:
                        raise Exception(f"OCR process failed with return code {process.returncode}")
                    
                    update_progress(file_id, 95, "Reading results...")
                    
                    output_path = f'{CWD}/temp_dir/output_ocr.json'
                    with open(output_path, 'r') as file:
                        result = json.loads(file.read().strip())
                    
                    ocr_text = result.get('text', '') or str(result)
                    
                    print(f"Successfully processed: {filename}")
                    print(f"Text preview: {ocr_text[:100]}...")
                    
                    update_status(file_id, 'completed', ocr_text=json.dumps(result))
                    
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Deleted image file: {filepath}")
                    
                except Exception as e:
                    print(f"Failed to process: {filename}")
                    print(f"Error: {str(e)}")
                    update_status(file_id, 'failed', error=str(e))
                    
            else:
                time.sleep(POLL_INTERVAL)
                
        except Exception as e:
            print(f"Worker error: {str(e)}")
            time.sleep(POLL_INTERVAL)

def update_progress(file_id, progress, progress_text=None):
    conn = sqlite3.connect('ocr_results.db')
    c = conn.cursor()
    c.execute('UPDATE image_files SET progress = ?, progress_text = ? WHERE id = ?',
              (progress, progress_text, file_id))
    conn.commit()
    conn.close()

def update_status(file_id, status, ocr_text=None, error=None):
    conn = sqlite3.connect('ocr_results.db')
    c = conn.cursor()
    
    if status == 'completed':
        c.execute('''UPDATE image_files 
                     SET status = ?, ocr_text = ?, processed_at = ?, progress = 100, progress_text = 'Completed'
                     WHERE id = ?''',
                  (status, ocr_text, datetime.now().isoformat(), file_id))
    elif status == 'failed':
        c.execute('''UPDATE image_files 
                     SET status = ?, ocr_text = ?, processed_at = ?, progress_text = 'Failed'
                     WHERE id = ?''',
                  (status, f"Error: {error}", datetime.now().isoformat(), file_id))
    else:
        c.execute('UPDATE image_files SET status = ? WHERE id = ?', (status, file_id))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
    file.save(filepath)
    
    hide_from_ui_str = request.form.get('hide_from_ui', '')
    hide_from_ui_val = 1 if str(hide_from_ui_str).lower() in ['true', '1'] else 0
    
    conn = sqlite3.connect('ocr_results.db')
    c = conn.cursor()
    c.execute('''INSERT INTO image_files 
                 (id, filename, filepath, status, created_at, hide_from_ui)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (file_id, filename, filepath, 'not_started', datetime.now().isoformat(), hide_from_ui_val))
    conn.commit()
    conn.close()
    
    start_worker()
    
    return jsonify({
        'id': file_id,
        'filename': filename,
        'status': 'not_started',
        'message': 'File uploaded successfully'
    }), 201

def get_average_processing_time(cursor):
    cursor.execute('''SELECT created_at, processed_at FROM image_files 
                      WHERE status = 'completed' AND processed_at IS NOT NULL
                      ORDER BY processed_at DESC LIMIT 20''')
    completed_rows = cursor.fetchall()
    
    if not completed_rows:
        return 30.0
    
    total_seconds = 0
    count = 0
    for r in completed_rows:
        try:
            created = datetime.fromisoformat(r['created_at'])
            processed = datetime.fromisoformat(r['processed_at'])
            duration = (processed - created).total_seconds()
            if duration > 0:
                total_seconds += duration
                count += 1
        except:
            continue
    
    return total_seconds / count if count > 0 else 30.0

@app.route('/api/files', methods=['GET'])
def get_files():
    conn = sqlite3.connect('ocr_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    avg_time = get_average_processing_time(c)
    
    c.execute('''SELECT id FROM image_files 
                 WHERE status = 'not_started' 
                 ORDER BY created_at ASC''')
    queue_ids = [row['id'] for row in c.fetchall()]
    
    c.execute('''SELECT COUNT(*) as count FROM image_files WHERE status = 'processing' ''')
    processing_count = c.fetchone()['count']
    
    c.execute('SELECT * FROM image_files WHERE hide_from_ui = 0 OR hide_from_ui IS NULL ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        queue_position = None
        estimated_start_seconds = None
        
        if row['status'] == 'not_started' and row['id'] in queue_ids:
            queue_position = queue_ids.index(row['id']) + 1
            files_ahead = queue_position - 1 + processing_count
            estimated_start_seconds = round(files_ahead * avg_time)
        
        files.append({
            'id': row['id'],
            'filename': row['filename'],
            'status': row['status'],
            'ocr_text': "HIDDEN_IN_LIST_VIEW",
            'created_at': row['created_at'],
            'processed_at': row['processed_at'],
            'progress': row['progress'] or 0,
            'progress_text': row['progress_text'],
            'queue_position': queue_position,
            'estimated_start_seconds': estimated_start_seconds
        })
    
    return jsonify(files)

@app.route('/api/files/<file_id>', methods=['GET'])
def get_file(file_id):
    conn = sqlite3.connect('ocr_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM image_files WHERE id = ?', (file_id,))
    row = c.fetchone()
    
    if row is None:
        conn.close()
        return jsonify({'error': 'File not found'}), 404
    
    queue_position = None
    estimated_start_seconds = None
    
    if row['status'] == 'not_started':
        avg_time = get_average_processing_time(c)
        
        c.execute('''SELECT COUNT(*) as position FROM image_files 
                     WHERE status = 'not_started' AND created_at < ?''',
                  (row['created_at'],))
        position_row = c.fetchone()
        queue_position = position_row['position'] + 1
        
        c.execute('''SELECT COUNT(*) as count FROM image_files WHERE status = 'processing' ''')
        processing_count = c.fetchone()['count']
        
        files_ahead = queue_position - 1 + processing_count
        estimated_start_seconds = round(files_ahead * avg_time)
    
    conn.close()
    
    return jsonify({
        'id': row['id'],
        'filename': row['filename'],
        'status': row['status'],
        'ocr_text': row['ocr_text'],
        'created_at': row['created_at'],
        'processed_at': row['processed_at'],
        'progress': row['progress'] or 0,
        'progress_text': row['progress_text'],
        'queue_position': queue_position,
        'estimated_start_seconds': estimated_start_seconds
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'ocr-runner',
        'worker_running': worker_running
    })

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("OCR Runner API Server")
    print("="*60)
    print("Worker will start automatically on first upload")
    print("Image files will be deleted after successful processing")
    print("="*60 + "\n")
    
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)