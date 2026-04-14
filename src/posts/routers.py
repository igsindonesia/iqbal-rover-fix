from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime, timezone
from starlette.requests import Request
from typing import List, Optional, Tuple

import uuid
import shutil
import cv2

from src.core.db import get_db
from src.core.auth import get_current_user
from src.core.config import settings
from src.yolo_detector.V11 import Yolov11Detector
from src.posts._utils import _read_yaml_file
from src.posts.models import Post

# Constants
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

router = APIRouter(prefix="/posts", tags=["Posts"])

detector: Optional[Yolov11Detector] = None
class_names: Optional[List[str]] = None


def _get_detector() -> Tuple[Yolov11Detector, List[str]]:
    global detector, class_names
    if detector is None or class_names is None:
        try:
            class_names = _read_yaml_file(str(settings.LABEL_PATH))
            detector = Yolov11Detector(
                model_path=settings.MODEL_PATH, label_yaml=settings.LABEL_PATH
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Detector initialization failed: {exc}",
            )
    return detector, class_names


# --- UPLOAD & PREDICT (TIDAK SIMPAN KE DB) ---
@router.post("/", status_code=status.HTTP_200_OK)
async def upload_and_predict(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),  # tetap butuh auth, tapi tidak butuh db
):
    # Validasi ekstensi
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Simpan file
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.{file_ext}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    detector_instance, loaded_class_names = _get_detector()

    # Deteksi
    img = cv2.imread(str(file_path))
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read uploaded image",
        )
    boxes, scores, class_ids = detector_instance.detect(img)

    # Format hasil
    if not boxes:
        result_predict = {"predict": {}, "confidence": {}, "bbox": {}}
    else:
        predict_summary = {}
        predict_confidence = {}
        predict_bbox = {}
        for box, score, cls_id in zip(boxes, scores, class_ids):
            cls_name = (
                loaded_class_names[cls_id]
                if cls_id < len(loaded_class_names)
                else f"class_{cls_id}"
            )
            predict_summary[cls_name] = predict_summary.get(cls_name, 0) + 1
            predict_confidence.setdefault(cls_name, []).append(round(float(score), 4))
            predict_bbox.setdefault(cls_name, []).append([int(x) for x in box])

        result_predict = {
            "predict": predict_summary,
            "confidence": predict_confidence,
            "bbox": predict_bbox,
        }

    # ✅ Hanya kembalikan data, TIDAK SIMPAN KE DATABASE
    return JSONResponse({"image_url": str(file_path), "result": result_predict})


@router.get("/history", status_code=status.HTTP_200_OK)
async def get_histroy(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    posts = (
        db.query(Post)
        .filter(Post.user_id == current_user.user_id)
        .order_by(Post.create_at.desc())
        .all()
    )
    history_by_user_all = []
    for post in posts:
        history_by_user_all.append(
            {
                "post_id": post.post_id,
                "image_url": post.image_url,
                "create_at": post.create_at.isoformat(),  # agar JSON-serializable
                "result": post.result or {},
            }
        )

    return JSONResponse(history_by_user_all)


# --- SIMPAN EDIT (YANG BENAR-BENAR SIMPAN KE DB) ---
@router.post("/simpan-edit")
async def simpan_edit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    form_data = await request.form()

    image_path = form_data.get("image_path")
    if not image_path:
        raise HTTPException(status_code=400, detail="image_path tidak ditemukan")

    semua_benar = form_data.get("semua_benar")

    # Ekstrak data dinamis
    class_labels = []
    counters = []
    i = 1
    while True:
        label = form_data.get(f"class_label_{i}")
        counter_str = form_data.get(f"counter_{i}")
        if label is None or counter_str is None:
            break
        try:
            counter = int(counter_str)
        except (ValueError, TypeError):
            counter = 1
        class_labels.append(label)
        counters.append(counter)
        i += 1

    # Simpan ke DB (hanya di sini!)
    from src.posts.models import Post  # pastikan diimpor

    new_post = Post(
        post_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        image_url=image_path,
        result={
            "labels": class_labels,
            "counters": counters,
        },  # atau format predict jika diinginkan
        create_at=datetime.now(timezone.utc),
        update_at=datetime.now(timezone.utc),
    )
    db.add(new_post)
    db.commit()

    return {"message": "Berhasil disimpan"}
