from flask import Flask, request, jsonify
import dropbox
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for your frontend domain (adjust URL to your Netlify/Qualtrics origin)
CORS(app, origins=["https://quiet-beignet-08bd46.netlify.app"])

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
