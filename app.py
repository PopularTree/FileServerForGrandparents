from flask import Flask, request, render_template, send_from_directory, redirect, url_for, abort
import os
from werkzeug.utils import secure_filename
from modules import Media, Session
from utils import (
    save_file, make_image_thumbnail, make_video_thumbnail,
    BASE_DIR, THUMB_DIR, get_photo_datetime, get_video_datetime
)
from sqlalchemy import func
import datetime

ALLOWED_IMAGE = {"png", "jpg", "jpeg", "gif"}
ALLOWED_VIDEO = {"mp4", "mov"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE | ALLOWED_VIDEO

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        files = request.files.getlist("file")
        session = Session()
        for file in files:
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue
            kind = "photos" if ext in ALLOWED_IMAGE else "videos"
            rel_path, abs_path = save_file(file, kind)
            # サムネイル生成
            thumb_name = os.path.basename(abs_path).rsplit(".", 1)[0] + ".jpg"
            thumb_path = os.path.join(THUMB_DIR, thumb_name)
            try:
                if kind == "photos":
                    make_image_thumbnail(abs_path, thumb_path)
                else:
                    make_video_thumbnail(abs_path, thumb_path)
            except Exception:
                pass
            # メタデータから撮影日時取得
            taken_at = None
            if kind == "photos":
                taken_at = get_photo_datetime(abs_path)
            else:
                taken_at = get_video_datetime(abs_path)
            # DB登録
            media = Media(
                filename=rel_path,
                original_name=file.filename,
                media_type="image" if kind == "photos" else "video",
                taken_at=taken_at
            )
            session.add(media)
        session.commit()
        session.close()
        return redirect(url_for("gallery"))
    return render_template("upload.html")

@app.route("/gallery", methods=["GET"])
def gallery():
    query = request.args.get("q", "")
    session = Session()
    if query:
        # 日付（例: "2025-10-05"）で検索
        try:
            date_obj = datetime.datetime.strptime(query, "%Y-%m-%d")
            medias = session.query(Media).filter(
                func.date(Media.taken_at) == query
            ).order_by(Media.taken_at.desc()).all()
        except ValueError:
            medias = session.query(Media).order_by(Media.taken_at.desc()).all()
    else:
        medias = session.query(Media).order_by(Media.taken_at.desc()).all()
    session.close()
    return render_template("gallery.html", medias=medias, query=query)

@app.route("/files/<path:filename>")
def files(filename):
    abs_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(abs_path):
        abort(404)
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)
    return send_from_directory(dir_name, file_name)

@app.route("/thumb/<filename>")
def thumb(filename):
    thumb_path = os.path.join(THUMB_DIR, filename)
    if not os.path.exists(thumb_path):
        abort(404)
    return send_from_directory(THUMB_DIR, filename)

# 旧list画面（必要なら残す）
@app.route("/list")
def file_list():
    storage_dir = os.path.join(BASE_DIR, "storage")
    files = []
    for root, dirs, fs in os.walk(storage_dir):
        for f in fs:
            files.append(os.path.relpath(os.path.join(root, f), BASE_DIR))
    return render_template("list.html", files=files)

@app.route("/download/<path:filename>")
def download_file(filename):
    abs_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(abs_path):
        abort(404)
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)
    return send_from_directory(dir_name, file_name, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
