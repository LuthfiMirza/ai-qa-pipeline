from __future__ import annotations

from pathlib import Path

import cv2
from skimage.metrics import structural_similarity as ssim


def compare_screenshots(baseline_path: str | Path, current_path: str | Path, diff_path: str | Path) -> dict[str, object]:
    baseline = cv2.imread(str(baseline_path))
    current = cv2.imread(str(current_path))
    if baseline is None:
        raise FileNotFoundError(f"Baseline image not found: {baseline_path}")
    if current is None:
        raise FileNotFoundError(f"Current image not found: {current_path}")

    if baseline.shape != current.shape:
        current = cv2.resize(current, (baseline.shape[1], baseline.shape[0]))

    baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    score, diff = ssim(baseline_gray, current_gray, full=True)
    diff = (diff * 255).astype("uint8")
    threshold = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated = current.copy()
    regions_changed = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        if width * height < 50:
            continue
        regions_changed.append({"x": x, "y": y, "width": width, "height": height})
        cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 0, 255), 2)

    diff_output = Path(diff_path)
    diff_output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(diff_output), annotated)
    return {"ssim_score": float(score), "diff_image": str(diff_output), "regions_changed": regions_changed}


def is_regression(ssim_score: float, threshold: float = 0.95) -> bool:
    return ssim_score < threshold
