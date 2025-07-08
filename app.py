from flask import Flask, request, jsonify
from flask_cors import CORS  #
import dropbox
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Inside upload_file():
timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
filename = f"voice_recording_{timestamp}.wav"

app = Flask(__name__)
CORS(app) 
# Load Dropbox credentials from environment variables
DROPBOX_APP_KEY = os.environ.get('DROPBOX_APP_KEY')
DROPBOX_APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')
DROPBOX_REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN')
def get_access_token():
    """Refreshes the Dropbox access token using the stored refresh token."""
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        auth=HTTPBasicAuth(DROPBOX_APP_KEY, DROPBOX_APP_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN
        }
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    original_filename = file.filename or f"unnamed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.wav"
    dropbox_path = f"/qualtrics_audio/{original_filename}"

    try:
       access_token = get_access_token()
        dbx = dropbox.Dropbox(access_token)

        file_content = file.read()
        dbx.files_upload(file_content, dropbox_path, mute=True)
        print(f"Uploading {filename}, size: {len(file_content)} bytes")
        return jsonify({'status': 'success', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
