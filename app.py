import os
import threading
import webbrowser

from flask import Flask, Response, request
from werkzeug.utils import secure_filename
from backend.ingestion.ingest import ingest_file
from backend.agent.agent import agent

app = Flask(__name__, static_folder="frontend", static_url_path="")
APP_URL = "http://127.0.0.1:5000/"
UPLOAD_DIR = os.path.join(app.root_path, "data")
RUNNING_IN_DOCKER = os.environ.get("RUNNING_IN_DOCKER") == "1"


def open_browser():
    webbrowser.open_new(APP_URL)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/favicon.ico")
def favicon():
    return ("", 204)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if file is None or not file.filename:
        return {"message": "No file provided"}, 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = secure_filename(file.filename) or "uploaded_document"
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)

    ingest_file(path)

    return {"message": "File processed", "filename": filename}

@app.route("/chat", methods=["POST"])
def chat():
    query = request.json["query"]

    def generate():
        response = agent.run(query)
        for word in response.split():
            yield word + " "

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    debug_mode = True
    should_open_browser = (
        os.environ.get("WERKZEUG_RUN_MAIN") == "true"
        if debug_mode
        else os.environ.get("WERKZEUG_RUN_MAIN") is None
    )

    if should_open_browser and not RUNNING_IN_DOCKER:
        threading.Timer(1.2, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
