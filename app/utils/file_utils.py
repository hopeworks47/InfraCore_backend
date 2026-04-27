import os
import shutil
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "uploads"

def ensure_upload_dir(path: str):
    os.makedirs(path, exist_ok=True)

async def save_image(file: UploadFile, folder: str='images') -> str:
    # Create full directory path
    dir_path = os.path.join(UPLOAD_DIR, folder)
    ensure_upload_dir(dir_path)

    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(dir_path, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return relative URL path
    return f"/uploads/{folder}/{filename}"

def delete_old_image(image_path: str):
    if image_path and os.path.exists(image_path.lstrip("/")):
        os.remove(image_path.lstrip("/"))