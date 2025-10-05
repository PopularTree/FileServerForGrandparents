# utils.py
import os, datetime, subprocess
from PIL import Image
import piexif
import json

BASE_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
THUMB_DIR = os.path.join(BASE_DIR, 'thumbnails')
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

def ensure_dirs(kind):
    d = os.path.join(STORAGE_DIR, kind, datetime.datetime.utcnow().strftime('%Y-%m-%d'))
    os.makedirs(d, exist_ok=True)
    return d

def save_file(file_storage, kind):
    # kind = 'photos' or 'videos'
    d = ensure_dirs(kind)
    ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    safe_name = f"{ts}_{file_storage.filename.replace(' ', '_')}"
    path = os.path.join(d, safe_name)
    file_storage.save(path)
    rel = os.path.relpath(path, BASE_DIR)
    return rel, path

def make_image_thumbnail(src_path, dest_path, size=(400,300)):
    im = Image.open(src_path)
    im.thumbnail(size)
    im.save(dest_path, format='JPEG')

def make_video_thumbnail(src_path, dest_path, time='00:00:01'):
    # use ffmpeg to grab a frame
    cmd = ['ffmpeg', '-y', '-i', src_path, '-ss', time, '-vframes', '1', dest_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_photo_datetime(path):
    try:
        exif_dict = piexif.load(path)
        dt_bytes = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
        if dt_bytes:
            dt_str = dt_bytes.decode('utf-8')
            # EXIFは "YYYY:MM:DD HH:MM:SS" 形式
            return datetime.datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def get_video_datetime(path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags=creation_time', path
    ]
    result = subprocess.run(cmd, capture_output=True)
    try:
        info = json.loads(result.stdout)
        dt_str = info['format']['tags']['creation_time']
        # 例: "2025-10-05T12:34:56.000000Z"
        return datetime.datetime.strptime(dt_str[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None
