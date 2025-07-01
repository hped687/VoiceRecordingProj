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
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"voice_recording_{timestamp}.wav"
    dropbox_path = f"/qualtrics_audio/{filename}"

    try:
        dbx.files_upload(file.read(), dropbox_path, mute=True)
        print(f"Uploading {filename}, size: {len(file.read())} bytes")
        return jsonify({'status': 'success', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
