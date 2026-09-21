from flask import Flask, request, jsonify
from flask_cors import CORS
import dropbox
from dropbox.files import WriteMode
import os
import time
import traceback
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://quiet-beignet-08bd46.netlify.app"])

DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

# One Dropbox client for the whole app. Giving it the refresh token lets the
# SDK refresh the access token by itself, only when it expires (every ~4 hours),
# instead of calling Dropbox's token endpoint on every single upload.
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET,
    timeout=60,
)


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    # For an uptime monitor to ping so the free Render server doesn't sleep
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload_file():
    started = time.time()
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename or "") or f"voice_recording_{timestamp}.wav"
        dropbox_path = f"/qualtrics_audio/{filename}"

        file_content = file.read()
        print(f"📥 Received {filename}, {len(file_content)} bytes", flush=True)

        if not file_content:
            return jsonify({"error": "Empty file"}), 400

        # Retry a couple of times in case Dropbox has a hiccup
        last_error = None
        for attempt in range(1, 4):
            try:
                dbx.files_upload(
                    file_content,
                    dropbox_path,
                    mode=WriteMode("add"),
                    autorename=True,  # never fail because a file of that name exists
                    mute=True,
                )
                print(f"✅ Uploaded {filename} in {time.time() - started:.1f}s", flush=True)
                return jsonify({"status": "success", "filename": filename}), 200
            except Exception as e:
                last_error = e
                print(f"⚠️ Dropbox attempt {attempt} failed: {e}", flush=True)
                time.sleep(attempt * 2)

        raise last_error

    except Exception as e:
        print("❌ Error during upload:", flush=True)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Make sure even unexpected errors come back as JSON (with CORS headers)
@app.errorhandler(Exception)
def handle_unexpected(e):
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
