import os
import shutil
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "uploads"

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_image(file: UploadFile, folder: str='images') -> str:
    ensure_upload_dir()
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Return relative path (or full URL)
    return f"/uploads/{folder}/{filename}"

def delete_old_image(image_path: str):
    if image_path and os.path.exists(image_path.lstrip("/")):
        os.remove(image_path.lstrip("/"))