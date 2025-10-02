from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/home/pi/media_storage"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# アップロード画面
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "ファイルが選択されていません", 400
        files = request.files.getlist("file")
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return redirect(url_for("file_list"))
    return render_template("upload.html")

# ファイル一覧
@app.route("/list")
def file_list():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("list.html", files=files)

# ダウンロード用
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
