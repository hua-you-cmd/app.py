"""
ボイスタイマー (Voice Timer) - Python完全版
========================================
【指定されたインターバルタイマーの全ルーティン】
1. スタート (20秒) ➔ ラスト3秒 「3, 2, 1」
2. 『休憩』 (10秒) ➔ ラスト3秒 「3, 2, 1」
3. 『スタート』 (20秒) ➔ ラスト3秒 「3, 2, 1」
4. 『休憩』 (5秒) ➔ ラスト3秒 「3, 2, 1」
5. 『準備』 (30秒) ➔ ラスト3秒 「3, 2, 1」
6. 『スタート』 (20秒) ➔ ラスト3秒 「3, 2, 1」
7. 『休憩』 (10秒) ➔ ラスト3秒 「3, 2, 1」
8. 『スタート』 (20秒) ➔ ラスト3秒 「3, 2, 1」
9. 終了時: 『頑張りました！お疲れ様でした！』

【セキュリティ・アクセス制御】
- 家族用パスコード: 0516
- 1日最大100回セッション制限付き
"""

import sys
import time
import datetime
import threading
import subprocess
import platform
import tkinter as tk
from tkinter import messagebox

# ---------------------------------------------------------
# 音声読み上げ Engine (Windows / macOS / Linux 対応)
# ---------------------------------------------------------
class SpeechEngine:
    def __init__(self):
        self.os_type = platform.system()
        self.pyttsx3_engine = None
        
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            voices = self.pyttsx3_engine.getProperty('voices')
            for voice in voices:
                if 'ja' in voice.id.lower() or 'japan' in voice.name.lower():
                    self.pyttsx3_engine.setProperty('voice', voice.id)
                    break
        except Exception:
            self.pyttsx3_engine = None

    def speak(self, text: str):
        """別スレッドで音声を発声"""
        def _say():
            try:
                if self.os_type == 'Darwin':  # macOS 標準スピーチ
                    subprocess.run(['say', '-v', 'Kyoko', text], check=False)
                elif self.os_type == 'Windows':  # Windows PowerShell/pyttsx3
                    if self.pyttsx3_engine:
                        self.pyttsx3_engine.say(text)
                        self.pyttsx3_engine.runAndWait()
                    else:
                        ps_cmd = f"Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('{text}')"
                        subprocess.run(["powershell", "-Command", ps_cmd], check=False)
                elif self.os_type == 'Linux':  # Linux (espeak / spd-say)
                    if self.pyttsx3_engine:
                        self.pyttsx3_engine.say(text)
                        self.pyttsx3_engine.runAndWait()
                    else:
                        subprocess.run(['spd-say', text], check=False)
                else:
                    if self.pyttsx3_engine:
                        self.pyttsx3_engine.say(text)
                        self.pyttsx3_engine.runAndWait()
            except Exception as e:
                print(f"[音声出力エラー]: {e}")

        threading.Thread(target=_say, daemon=True).start()

# ---------------------------------------------------------
# 1日100回制限 ＆ セキュリティ管理クラス
# ---------------------------------------------------------
class FamilySecurityManager:
    PASSCODE = "0516"
    MAX_DAILY_SESSIONS = 100

    def __init__(self):
        self.current_date = datetime.date.today()
        self.daily_session_count = 0

    def check_reset(self):
        today = datetime.date.today()
        if today != self.current_date:
            self.current_date = today
            self.daily_session_count = 0

    def verify_passcode(self, pin: str) -> bool:
        return pin == self.PASSCODE

    def can_start_session(self) -> bool:
        self.check_reset()
        return self.daily_session_count < self.MAX_DAILY_SESSIONS

    def record_session(self):
        self.check_reset()
        self.daily_session_count += 1

# ---------------------------------------------------------
# 全8ステップ タイマー構成定義
# ---------------------------------------------------------
ROUTINE_PHASES = [
    {"label": "スタート", "seconds": 20, "announce": "スタート"},
    {"label": "休憩",     "seconds": 10, "announce": "休憩"},
    {"label": "スタート", "seconds": 20, "announce": "スタート"},
    {"label": "休憩",     "seconds": 5,  "announce": "休憩"},
    {"label": "準備",     "seconds": 30, "announce": "準備"},
    {"label": "スタート", "seconds": 20, "announce": "スタート"},
    {"label": "休憩",     "seconds": 10, "announce": "休憩"},
    {"label": "スタート", "seconds": 20, "announce": "スタート"},
]

# ---------------------------------------------------------
# GUI アプリケーション (Tkinter)
# ---------------------------------------------------------
class VoiceTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ボイスタイマー - 家族専用 (Python版)")
        self.root.geometry("460x620")
        self.root.configure(bg="#0f172a")

        self.speech = SpeechEngine()
        self.security = FamilySecurityManager()

        self.is_authenticated = False
        self.is_running = False
        self.is_paused = False
        self.current_phase_idx = 0
        self.seconds_remaining = ROUTINE_PHASES[0]["seconds"]

        self._build_auth_ui()

    def _build_auth_ui(self):
        """パスコード入力画面 (ロック画面)"""
        self.auth_frame = tk.Frame(self.root, bg="#0f172a", padx=20, pady=40)
        self.auth_frame.pack(fill="both", expand=True)

        title_label = tk.Label(
            self.auth_frame,
            text="🔒 家族専用アクセス保護",
            font=("Helvetica", 18, "bold"),
            fg="#10b981",
            bg="#0f172a"
        )
        title_label.pack(pady=10)

        sub_label = tk.Label(
            self.auth_frame,
            text="パスコードを入力して解除してください\n(初期設定: 0516 / 1日100回制限付き)",
            font=("Helvetica", 10),
            fg="#94a3b8",
            bg="#0f172a"
        )
        sub_label.pack(pady=5)

        self.pin_entry = tk.Entry(
            self.auth_frame,
            font=("Courier", 20, "bold"),
            show="*",
            justify="center",
            width=10,
            bg="#1e293b",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.pin_entry.pack(pady=20)
        self.pin_entry.focus()

        unlock_btn = tk.Button(
            self.auth_frame,
            text="ロック解除",
            font=("Helvetica", 12, "bold"),
            bg="#10b981",
            fg="#0f172a",
            activebackground="#34d399",
            padx=20,
            pady=8,
            command=self._handle_login
        )
        unlock_btn.pack(pady=10)

    def _handle_login(self):
        pin = self.pin_entry.get().strip()
        if self.security.verify_passcode(pin):
            self.is_authenticated = True
            self.auth_frame.destroy()
            self._build_timer_ui()
        else:
            messagebox.showerror("エラー", "パスコードが正しくありません。(初期設定: 0516)")

    def _build_timer_ui(self):
        """メインタイマー画面"""
        self.main_frame = tk.Frame(self.root, bg="#0f172a", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # ヘッダー情報
        header_frame = tk.Frame(self.main_frame, bg="#1e293b", padx=10, pady=8)
        header_frame.pack(fill="x", pady=5)

        self.status_info_label = tk.Label(
            header_frame,
            text=f"🛡️ 家族専用モード | 本日の利用: {self.security.daily_session_count}/{self.security.MAX_DAILY_SESSIONS}回",
            font=("Helvetica", 9, "bold"),
            fg="#34d399",
            bg="#1e293b"
        )
        self.status_info_label.pack()

        # ステップ表示
        self.phase_badge = tk.Label(
            self.main_frame,
            text="準備完了",
            font=("Helvetica", 14, "bold"),
            fg="#10b981",
            bg="#0f172a",
            pady=10
        )
        self.phase_badge.pack()

        # カウントダウン表示
        self.timer_label = tk.Label(
            self.main_frame,
            text="20",
            font=("Helvetica", 72, "bold"),
            fg="#ffffff",
            bg="#0f172a"
        )
        self.timer_label.pack(pady=10)

        # 音声案内ログ
        self.voice_log_label = tk.Label(
            self.main_frame,
            text="『スタートボタンを押してください』",
            font=("Helvetica", 11, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        self.voice_log_label.pack(pady=5)

        # 操作ボタン
        btn_frame = tk.Frame(self.main_frame, bg="#0f172a")
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(
            btn_frame,
            text="スタート",
            font=("Helvetica", 14, "bold"),
            bg="#10b981",
            fg="#0f172a",
            width=10,
            pady=8,
            command=self.start_timer
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            btn_frame,
            text="一時停止",
            font=("Helvetica", 12, "bold"),
            bg="#f59e0b",
            fg="#0f172a",
            width=8,
            pady=8,
            state="disabled",
            command=self.toggle_pause
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="ストップ",
            font=("Helvetica", 12, "bold"),
            bg="#ef4444",
            fg="#ffffff",
            width=8,
            pady=8,
            state="disabled",
            command=self.stop_timer
        )
        self.stop_btn.grid(row=0, column=2, padx=5)

        # ルーティン一覧
        routine_box = tk.LabelFrame(
            self.main_frame,
            text="全8ステップ・ルーティン概要",
            font=("Helvetica", 9, "bold"),
            fg="#94a3b8",
            bg="#0f172a",
            padx=10,
            pady=5
        )
        routine_box.pack(fill="x", pady=10)

        routine_text = (
            "1. スタート (20s)  ➜  2. 休憩 (10s)\n"
            "3. スタート (20s)  ➜  4. 休憩 (5s)\n"
            "5. 準備 (30s)      ➜  6. スタート (20s)\n"
            "7. 休憩 (10s)      ➜  8. スタート (20s)"
        )
        tk.Label(
            routine_box,
            text=routine_text,
            font=("Courier", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            justify="left"
        ).pack()

    def start_timer(self):
        if not self.security.can_start_session():
            messagebox.showwarning("利用上限", "本日の利用上限(100回)に達しました。明日0時にリセットされます。")
            return

        self.security.record_session()
        self.status_info_label.config(
            text=f"🛡️ 家族専用モード | 本日の利用: {self.security.daily_session_count}/{self.security.MAX_DAILY_SESSIONS}回"
        )

        self.is_running = True
        self.is_paused = False
        self.current_phase_idx = 0
        self.seconds_remaining = ROUTINE_PHASES[0]["seconds"]

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="一時停止")
        self.stop_btn.config(state="normal")

        # 第1フェーズ『スタート』アナウンス
        self._announce("スタート")
        
        # タイマースレッド起動
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.config(text="一時停止")
        else:
            self.is_paused = True
            self.pause_btn.config(text="再開")

    def stop_timer(self):
        self.is_running = False
        self.is_paused = False
        self.timer_label.config(text="20", fg="#ffffff")
        self.phase_badge.config(text="リセット完了", fg="#10b981")
        self.voice_log_label.config(text="『スタートボタンを押してください』")

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="一時停止")
        self.stop_btn.config(state="disabled")

    def _announce(self, text: str):
        """UI更新と音声読み上げ"""
        self.voice_log_label.config(text=f"『{text}』")
        self.speech.speak(text)

    def _timer_loop(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.2)
                continue

            current_phase = ROUTINE_PHASES[self.current_phase_idx]
            
            # UI更新 (フェーズ表示)
            self.root.after(0, self.phase_badge.config, {
                "text": f"ステップ {self.current_phase_idx + 1}/8: {current_phase['label']}",
                "fg": "#10b981" if current_phase["label"] == "スタート" else "#38bdf8" if current_phase["label"] == "休憩" else "#f59e0b"
            })

            # カウントダウン表示更新
            sec = self.seconds_remaining
            self.root.after(0, self.timer_label.config, {
                "text": f"{sec:02d}",
                "fg": "#f43f5e" if sec <= 3 else "#ffffff"
            })

            # 残り3, 2, 1秒の音声読み上げ
            if sec in [3, 2, 1]:
                self._announce(str(sec))

            time.sleep(1.0)
            self.seconds_remaining -= 1

            if self.seconds_remaining <= 0:
                # 次のステップへ
                self.current_phase_idx += 1
                if self.current_phase_idx < len(ROUTINE_PHASES):
                    next_phase = ROUTINE_PHASES[self.current_phase_idx]
                    self.seconds_remaining = next_phase["seconds"]
                    # 『休憩』『スタート』『準備』アナウンス
                    self._announce(next_phase["announce"])
                else:
                    # 全ルーティン完走
                    self.is_running = False
                    self.root.after(0, self._finish_routine)
                    break

    def _finish_routine(self):
        self.timer_label.config(text="完了", fg="#10b981")
        self.phase_badge.config(text="🎉 全ルーティン完走！", fg="#34d399")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        
        # 最終完了アナウンス
        self._announce("頑張りました！お疲れ様でした！")

# ---------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTimerApp(root)
    root.mainloop()
