from flask import Flask, request, jsonify
from flask_cors import CORS
import dropbox
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import traceback

app = Flask(__name__)
CORS(app)

# Environment variables
DROPBOX_APP_KEY = os.environ.get('DROPBOX_APP_KEY')
DROPBOX_APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')
DROPBOX_REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN')

def get_access_token():
    print("🔁 Refreshing access token...")
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        auth=HTTPBasicAuth(DROPBOX_APP_KEY, DROPBOX_APP_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN
        }
    )
    if response.ok:
        print("✅ Access token refreshed.")
        return response.json()['access_token']
    else:
        print("❌ Failed to refresh access token:", response.text)
        raise Exception(f"Token refresh failed: {response.text}")

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        original_filename = file.filename or f"voice_recording_{timestamp}.wav"
        filename = secure_filename(original_filename)
        dropbox_path = f"/qualtrics_audio/{filename}"

        print(f"📥 File received: {filename}")

        access_token = get_access_token()
        dbx = dropbox.Dropbox(access_token)

        file_content = file.read()
        print(f"📤 Uploading {filename}, size: {len(file_content)} bytes")

        dbx.files_upload(file_content, dropbox_path, mute=True)

        return jsonify({'status': 'success', 'filename': filename}), 200

    except Exception as e:
        print("❌ Error during upload:")
        traceback.print_exc()  # Print full stack trace
        return jsonify({'error': str(e)}), 500
