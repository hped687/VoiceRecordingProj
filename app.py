from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 Add this line
import dropbox
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # 👈 Enable CORS for all domains (or restrict to Netlify if preferred)

DROPBOX_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    dropbox_path = f"/qualtrics_audio/{filename}"

    try:
        dbx.files_upload(file.read(), dropbox_path, mute=True)
        return jsonify({'status': 'success', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    dropbox_path = f"/qualtrics_audio/{filename}"

    try:
        content = file.read()
        print(f"Uploading {filename}, size: {len(content)} bytes")
        dbx.files_upload(content, dropbox_path, mute=True)
        return jsonify({'status': 'success', 'filename': filename}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()  # <-- print full error trace to Render logs
        return jsonify({'error': str(e)}), 500
