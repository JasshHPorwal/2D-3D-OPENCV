import os
import cv2
import numpy as np


class ViewDetectionError(Exception):
    pass


def _iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    au = (ax2 - ax1) * (ay2 - ay1)
    bu = (bx2 - bx1) * (by2 - by1)
    return inter / (au + bu - inter)


def process(image_bytes: bytes, job_id: str, upload_dir: str) -> dict[str, np.ndarray]:
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ViewDetectionError('Invalid image')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(2.0, (8, 8)).apply(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0.8)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = bw.shape
    boxes = []
    for c in contours:
        if cv2.contourArea(c) > h * w * 0.01:
            x, y, bwc, bhc = cv2.boundingRect(c)
            boxes.append((x, y, x + bwc, y + bhc))
    merged = []
    for b in boxes:
        hit = False
        for i, m in enumerate(merged):
            if _iou(b, m) > 0.1:
                merged[i] = (min(b[0], m[0]), min(b[1], m[1]), max(b[2], m[2]), max(b[3], m[3]))
                hit = True
        if not hit:
            merged.append(b)
    if not merged:
        raise ViewDetectionError('No views detected')
    mx, my = w / 2, h / 2
    out = {}
    if len(merged) == 2:
        for b in merged:
            cx = (b[0] + b[2]) / 2
            out['front' if cx < mx else 'side'] = b
    else:
        for b in merged:
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            if cy < my and cx < mx:
                out['top'] = b
            elif cy >= my and cx < mx:
                out['front'] = b
            elif cy >= my and cx >= mx:
                out['side'] = b
    crops = {}
    dbg = os.path.join(upload_dir, job_id, 'debug')
    os.makedirs(dbg, exist_ok=True)
    for k, (x1, y1, x2, y2) in out.items():
        p = 20
        x1, y1, x2, y2 = max(0, x1 - p), max(0, y1 - p), min(w, x2 + p), min(h, y2 + p)
        c = img[y1:y2, x1:x2]
        crops[k] = c
        cv2.imwrite(os.path.join(dbg, f'{k}.png'), c)
    return crops
