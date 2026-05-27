import cv2
import numpy as np
import csv
import os

# --- Settings ---
VIDEO_PATH = "recording_2026-05-01.3TR.6.avi"
OUTPUT_DIR = "./output_results"

# Thresholds
THRESHOLD_VALUE = 50
MIN_AREA = 2000  # ノイズ除去用の最小面積

# ROI マージン
MARGIN_TOP = 100
MARGIN_BOTTOM = 100
MARGIN_LEFT = 150
MARGIN_RIGHT = 150

ALPHA = 0.7

# --- Video Load ---
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError(f"動画を開けません: {VIDEO_PATH}")

# --- CSV Setup ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
video_name = os.path.splitext(os.path.basename(VIDEO_PATH))[0]
csv_path = os.path.join(OUTPUT_DIR, f"{video_name}_contour.csv")

# --- Main Loop ---
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Frame", "Area", "Width", "Height"]) # グラフ作成用

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        h, w = frame.shape[:2]

        # 前処理（二値化）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(
            gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV
        )

        # マスク処理（ROI外のノイズカット）
        mask = np.zeros_like(binary)
        mask[
            MARGIN_TOP : h - MARGIN_BOTTOM,
            MARGIN_LEFT : w - MARGIN_RIGHT
        ] = 255
        binary = cv2.bitwise_and(binary, mask)

        # 輪郭抽出
        cnts = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_NONE
        )
        contours = cnts[0] if len(cnts) == 2 else cnts[1]

        if len(contours) == 0:
            cv2.imshow("Droplet outer contour only", frame)
            if cv2.waitKey(30) & 0xFF in [ord("q"), 27]:
                break
            continue

        # 面積でフィルタリング
        contours = [c for c in contours if cv2.contourArea(c) >= MIN_AREA]
        if len(contours) == 0:
            cv2.imshow("Droplet outer contour only", frame)
            if cv2.waitKey(30) & 255 in [ord("q"), 27]:
                break
            continue

        # 一番大きい輪郭（液滴）を選択
        droplet_contour = max(contours, key=cv2.contourArea)

        # データの算出
        x, y, w_box, h_box = cv2.boundingRect(droplet_contour)
        area = cv2.contourArea(droplet_contour)

        # CSV書き込み
        writer.writerow([frame_id, area, w_box, h_box])

        # 描画処理
        overlay = frame.copy()
        cv2.drawContours(overlay, [droplet_contour], -1, (0, 0, 255), thickness=1)
        result = cv2.addWeighted(overlay, ALPHA, frame, 1 - ALPHA, 0)

        cv2.imshow("Droplet outer contour only", result)

        if cv2.waitKey(30) & 0xFF in [ord("q"), 27]:
            break

# --- 終了処理 ---
cap.release()
cv2.destroyAllWindows()
print("CSV saved to:", csv_path)
