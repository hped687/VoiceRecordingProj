from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 Add this line
import dropbox
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Inside upload_file():
timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
filename = f"voice_recording_{timestamp}.wav"

app = Flask(__name__)
CORS(app) 
DROPBOX_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    original_filename = file.filename or f"unnamed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.wav"
    dropbox_path = f"/qualtrics_audio/{original_filename}"

    try:
        file_content = file.read()
        dbx.files_upload(file_content, dropbox_path, mute=True)
        print(f"Uploading {original_filename}, size: {len(file_content)} bytes")
        return jsonify({'status': 'success', 'filename': original_filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
