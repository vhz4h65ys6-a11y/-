import pyvisa
import time
import sys

# =========================
# 実験制御設定（計測器設定）
# =========================
# Created on May 27, 2026
# @author: M.Miyashita

VISA_ADDRESS = "USB0::0x0699::0x0353::2042364::0::INSTR"
CH = 2              # 使用するチャンネル（Channel 2）
VOLTAGE = 1.0       # 印加電圧 [V]
START_FREQ = 79     # 開始周波数 [Hz]
STOP_FREQ = 119     # 終了周波数 [Hz]
DWELL_TIME = 3      # 各周波数の保持時間 [s]

# =========================
# メイン処理（自動制御制御）
# =========================
def main():
    # 接続マネージャーの初期化
    rm = pyvisa.ResourceManager()
    print(f"Searching resources... Found: {rm.list_resources()}")

    try:
        # 計測器への接続
        inst = rm.open_resource(VISA_ADDRESS)
        print(f"Successfully connected to: {inst.query('*IDN?').strip()}")
    except Exception as e:
        print(f"Connection Error: {e}")
        sys.exit(1)

    # ファンクションジェネレータの初期設定
    inst.write(f"SOUR{CH}:FUNC SIN")       # 正弦波（Sin波）
    inst.write(f"SOUR{CH}:VOLT {VOLTAGE}")   # 電圧設定
    inst.write(f"OUTPUT{CH}:STATE ON")     # 出力開始
    print(f"Channel {CH} output initialized (Sin, {VOLTAGE}V).")

    # 周波数ステップスイープの自動実行
    print(f"Starting sweep: {START_FREQ} Hz -> {STOP_FREQ} Hz")
    
    try:
        for freq in range(START_FREQ, STOP_FREQ + 1):
            inst.write(f"SOUR{CH}:FREQ {freq}")
            print(f"[Sweeping] Current Frequency: {freq} Hz")
            time.sleep(DWELL_TIME)
            
    except KeyboardInterrupt:
        print("\nSweep interrupted by user.")
        
    finally:
        # 安全のため、終了時やエラー時は必ず出力をOFFにする
        inst.write(f"OUTP{CH} OFF")
        print("Experiment finished. Output turned OFF.")

if __name__ == "__main__":
    main()
