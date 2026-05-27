import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

# --- Settings ---
# ※公開用に相対パスに変更しています。
BASE_DIR = "./output_results"

CSV_FILES = [
    "recording_2026-04-27test3u.1_contour.csv",
    "recording_2026-04-27test3u.2_contour.csv",
    "recording_2026-04-27test3u.3_contour.csv",
]

DURATION_SEC = 124
SILENT_SEC = 10

# 周波数掃引範囲
FREQ_START = 79
FREQ_END   = 119
DWELL_SEC  = 3
MAX_POINTS = 4000

# 共振周波数の縦線位置
TARGET_FREQ = 99

# Font sizes
LABEL_FONTSIZE = 18
TICK_FONTSIZE = 14
LEGEND_FONTSIZE = 14
TITLE_FONTSIZE = 20

DATA_LINEWIDTH = 0.8
FREQ_LINEWIDTH = 0.8
VLINE_WIDTH = 1.0

OFFSET_STEP = 0.08

# --- Output Name Setup ---
first_name = os.path.splitext(CSV_FILES[0])[0]
first_name = re.sub(r'\.\d+_contour$', '', first_name)
out_png = os.path.join(BASE_DIR, first_name + "_compare_WidthHeightRatio_offset.png")

# --- Functions ---
def stepwise_frequency(t, f_start, f_end, dwell, silent_sec):
    shifted_t = t - silent_sec
    step = np.floor(shifted_t / dwell).astype(int)
    f = f_start + step
    f = np.where(t < silent_sec, f_start, f)
    return np.clip(f, f_start, f_end)

def downsample(x, y, max_points):
    n = len(x)
    if n <= max_points:
        return x, y
    step = max(1, n // max_points)
    return x[::step], y[::step]

def extract_exp_label(filename):
    m = re.search(r'\.(\d+)_contour', filename)
    if m:
        return f"Exp. {m.group(1)}"
    return os.path.splitext(filename)[0]

# --- Plot Main ---
fig, ax1 = plt.subplots(figsize=(10, 5))
all_y = []
plotted_count = 0

# CSVデータの読み込みとプロット
for i, csv_file in enumerate(CSV_FILES):
    csv_path = os.path.join(BASE_DIR, csv_file)

    if not os.path.exists(csv_path):
        print("WARNING:", csv_path, "not found.")
        continue

    df = pd.read_csv(csv_path)

    width = df["Width"].to_numpy(dtype=float)
    height = df["Height"].to_numpy(dtype=float)
    height = np.where(height == 0, np.nan, height)

    # アスペクト比の計算とオフセット追加
    y = width / height
    y = y + i * OFFSET_STEP

    n = len(y)
    time = np.linspace(0, DURATION_SEC, n)
    tp, yp = downsample(time, y, MAX_POINTS)

    ax1.plot(
        tp,
        yp,
        label=f"{extract_exp_label(csv_file)} (+{i*OFFSET_STEP:.2f})",
        linewidth=DATA_LINEWIDTH,
        alpha=0.8
    )

    all_y.extend(yp[np.isfinite(yp)])
    plotted_count += 1

# 左軸の設定（アスペクト比）
ax1.set_xlabel("Time [s]", fontsize=LABEL_FONTSIZE)
ax1.set_ylabel("Offset Width / Height [-]", fontsize=LABEL_FONTSIZE)
ax1.tick_params(axis="both", labelsize=TICK_FONTSIZE)
ax1.grid(True, linewidth=0.3, alpha=0.3)
ax1.set_title("Width / Height of 3 Experiments", fontsize=TITLE_FONTSIZE)

if len(all_y) > 0:
    ymin = np.min(all_y)
    ymax = np.max(all_y)
    margin = (ymax - ymin) * 0.15
    ax1.set_ylim(ymin - margin, ymax + margin)

# 共振周波数の位置に縦線を描画
target_time = SILENT_SEC + (TARGET_FREQ - FREQ_START) * DWELL_SEC
ax1.axvline(
    x=target_time,
    color="black",
    linestyle="--",
    linewidth=VLINE_WIDTH
)

ax1.annotate(
    f"Resonance frequency\n{TARGET_FREQ} Hz",
    xy=(target_time, 0.98),
    xycoords=("data", "axes fraction"),
    xytext=(6, 0),
    textcoords="offset points",
    ha="left",
    va="top",
    fontsize=9
)

# 右軸の設定（周波数ライン）
time_freq = np.linspace(0, DURATION_SEC, MAX_POINTS)
freq = stepwise_frequency(
    time_freq,
    FREQ_START,
    FREQ_END,
    DWELL_SEC,
    SILENT_SEC
)

ax2 = ax1.twinx()
ax2.plot(
    time_freq,
    freq,
    label="Frequency",
    linewidth=FREQ_LINEWIDTH,
    alpha=0.5
)
ax2.set_ylabel("Frequency [Hz]", fontsize=LABEL_FONTSIZE)
ax2.tick_params(axis="y", labelsize=TICK_FONTSIZE)
ax2.set_ylim(FREQ_START - 2, FREQ_END + 2)

# 凡例の結合表示
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    fontsize=LEGEND_FONTSIZE,
    loc="upper left"
)

# 保存処理
plt.tight_layout()
plt.savefig(out_png, dpi=300)
plt.show()
plt.close()

print("DONE:", out_png)
print("Plotted CSV count:", plotted_count)
