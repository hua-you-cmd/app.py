
# ==========================================
# FILE: tokeyi.py
# ==========================================

"""
GMO / SBI FX クオンツAI予測ダッシュボード (tokeyi.py - 完全独立スタンドアロン版)
Yahoo Financeから主要10通貨ペアデータをリアルタイム取得し、
機械学習(RandomForest)とテクニカル指標(SMA, RSI, MACD, ATR, Bollinger)から目標pips到達確率を算出・可視化します。
【新機能】予測精度トラッカー(Prediction Tracker) & 継続的再学習(Continual Learning)を搭載。
"""

import os
import json
import logging
import math
import smtplib
import urllib.request
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import numpy as np

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
import streamlit as st
import plotly.graph_objects as go

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. SBI / GMO為替メインレート 10通貨ペアの定義
SBI_PAIRS = [
    {"symbol": "AUDUSD=X", "ticker": "AUDUSD=X", "name": "AUD/USD", "disp": "豪ドル/米ドル", "type": "USD", "pip_scale": 0.0001, "target_pips": 250},
    {"symbol": "USDJPY=X", "ticker": "USDJPY=X", "name": "USD/JPY", "disp": "米ドル/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "EURJPY=X", "ticker": "EURJPY=X", "name": "EUR/JPY", "disp": "ユーロ/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "GBPJPY=X", "ticker": "GBPJPY=X", "name": "GBP/JPY", "disp": "ポンド/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "AUDJPY=X", "ticker": "AUDJPY=X", "name": "AUD/JPY", "disp": "豪ドル/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "NZDJPY=X", "ticker": "NZDJPY=X", "name": "NZD/JPY", "disp": "NZドル/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "CADJPY=X", "ticker": "CADJPY=X", "name": "CAD/JPY", "disp": "カナダドル/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "CHFJPY=X", "ticker": "CHFJPY=X", "name": "CHF/JPY", "disp": "スイスフラン/円", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    {"symbol": "GBPUSD=X", "ticker": "GBPUSD=X", "name": "GBP/USD", "disp": "ポンド/米ドル", "type": "USD", "pip_scale": 0.0001, "target_pips": 250},
    {"symbol": "EURUSD=X", "ticker": "EURUSD=X", "name": "EUR/USD", "disp": "ユーロ/米ドル", "type": "USD", "pip_scale": 0.0001, "target_pips": 250}
]

GMO_PAIRS = {pair["name"]: pair for pair in SBI_PAIRS}
TARGET_PAIRS = SBI_PAIRS
HISTORY_FILE = "prediction_history.csv"


# --- 2. 予測ログ蓄積・答え合わせ (Outcome Evaluator) & CSV管理モジュール ---
def load_prediction_history() -> pd.DataFrame:
    """保存された予測ログ履歴を読み込む"""
    cols = ["id", "timestamp", "pair_name", "price", "target_pips", "pred_direction", "long_prob", "short_prob", "outcome", "evaluated_at"]
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            for col in cols:
                if col not in df.columns:
                    df[col] = None
            return df
        except Exception as e:
            logging.error(f"Failed to load prediction history CSV: {e}")
    return pd.DataFrame(columns=cols)


def save_prediction_history(df: pd.DataFrame):
    """予測ログ履歴をCSVに保存"""
    try:
        df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        logging.error(f"Failed to save prediction history CSV: {e}")


def record_current_predictions(results: list, target_pips: float):
    """現在の予測結果をログに保存"""
    df_hist = load_prediction_history()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_rows = []

    for r in results:
        pair_name = r["name"]
        price = r["price"]
        long_p = r["long_prob"]
        short_p = r["short_prob"]

        if long_p >= short_p:
            pred_dir = "Long"
        else:
            pred_dir = "Short"

        # 重複追記を避ける（直近5分以内の同一ペアのログはスキップ）
        if not df_hist.empty:
            recent_same = df_hist[(df_hist["pair_name"] == pair_name) & (df_hist["timestamp"] > (pd.to_datetime(now_str) - pd.Timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"))]
            if not recent_same.empty:
                continue

        rec_id = f"{pair_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(df_hist) + len(new_rows) + 1}"
        new_rows.append({
            "id": rec_id,
            "timestamp": now_str,
            "pair_name": pair_name,
            "price": price,
            "target_pips": target_pips,
            "pred_direction": pred_dir,
            "long_prob": long_p,
            "short_prob": short_p,
            "outcome": -1, # -1: 未確定, 1: 勝ち, 0: 負け
            "evaluated_at": ""
        })

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_updated = pd.concat([df_hist, df_new], ignore_index=True)
        save_prediction_history(df_updated)
        return len(new_rows)
    return 0


def evaluate_prediction_outcomes(pairs_data_map: dict) -> pd.DataFrame:
    """
    過去の未確定予測ログに対し、実際の最新チャートデータから答え合わせ（正解判定）を行う。
    - Longの場合: 予測日以降の最高値 >= 予測時価格 + (target_pips * pip_scale) なら 勝ち (1)
    - Shortの場合: 予測日以降の最安値 <= 予測時価格 - (target_pips * pip_scale) なら 勝ち (1)
    - 期限切れ(15営業日経過)かつ未達成なら 負け (0)
    """
    df_hist = load_prediction_history()
    if df_hist.empty:
        return df_hist

    updated = False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for idx, row in df_hist.iterrows():
        if row["outcome"] != -1 and not pd.isna(row["outcome"]):
            continue # すでに確定済み

        pair_name = row["pair_name"]
        pred_time = pd.to_datetime(row["timestamp"])
        entry_price = float(row["price"])
        target_pips = float(row["target_pips"]) if not pd.isna(row["target_pips"]) else 250.0
        pred_dir = str(row["pred_direction"])

        pair_config = GMO_PAIRS.get(pair_name)
        if not pair_config:
            continue

        pip_scale = pair_config["pip_scale"]
        target_val = target_pips * pip_scale

        if pair_name in pairs_data_map and not pairs_data_map[pair_name].empty:
            chart_df = pairs_data_map[pair_name]
            # 予測日時以降のローソク足を抽出
            sub_df = chart_df[chart_df.index >= pred_time]
            if len(sub_df) < 1:
                continue

            max_high = sub_df["High"].max()
            min_low = sub_df["Low"].min()

            if pred_dir == "Long":
                if (max_high - entry_price) >= target_val:
                    df_hist.at[idx, "outcome"] = 1
                    df_hist.at[idx, "evaluated_at"] = now_str
                    updated = True
                elif len(sub_df) >= 15:
                    df_hist.at[idx, "outcome"] = 0
                    df_hist.at[idx, "evaluated_at"] = now_str
                    updated = True
            elif pred_dir == "Short":
                if (entry_price - min_low) >= target_val:
                    df_hist.at[idx, "outcome"] = 1
                    df_hist.at[idx, "evaluated_at"] = now_str
                    updated = True
                elif len(sub_df) >= 15:
                    df_hist.at[idx, "outcome"] = 0
                    df_hist.at[idx, "evaluated_at"] = now_str
                    updated = True

    if updated:
        save_prediction_history(df_hist)

    return df_hist


# --- 3. メール送信機能 (完全インライン独立関数) ---
def send_smtp_email(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    receiver_email: str = "huashenfo@gmail.com",
    subject: str = "",
    body_html: str = ""
) -> bool:
    """SMTPサーバーを利用してHTMLメールを送信"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        html_part = MIMEText(body_html, "html", "utf-8")
        msg.attach(html_part)

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

        logging.info(f"Email successfully sent to {receiver_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False


def build_signal_email_html(signals_df: pd.DataFrame, threshold_pct: float = 65.0) -> str:
    """メール通知用のHTMLボディを生成"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows_html = ""
    for idx, row in signals_df.iterrows():
        is_highlight = row.get("long_prob", 0) >= threshold_pct or row.get("short_prob", 0) >= threshold_pct
        bg_style = "background-color: #f0fdf4;" if is_highlight else ""
        
        rows_html += f"""
        <tr style="{bg_style} border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 10px; font-weight: bold;">{row.get('name', '')} ({row.get('display_name', '')})</td>
            <td style="padding: 10px; color: #2563eb; font-weight: bold;">{row.get('price', 0)}</td>
            <td style="padding: 10px; color: #16a34a; font-weight: bold;">{row.get('long_prob', 0)}%</td>
            <td style="padding: 10px; color: #dc2626; font-weight: bold;">{row.get('short_prob', 0)}%</td>
            <td style="padding: 10px;">{row.get('rsi', 50)}</td>
            <td style="padding: 10px;">{row.get('atr_pips', 0)} pips</td>
        </tr>
        """

    return f"""
    <div style="font-family: sans-serif; max-width: 650px; margin: auto; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px;">
        <h2 style="color: #1e3a8a;">📈 GMO / SBI FX クオンツAI 到達確率通知</h2>
        <p style="color: #6b7280; font-size: 13px;">計測日時: {now_str}</p>
        <p>送信先: huashenfo@gmail.com</p>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
            <thead>
                <tr style="background-color: #1e293b; color: white;">
                    <th style="padding: 10px;">通貨ペア</th>
                    <th style="padding: 10px;">現在値</th>
                    <th style="padding: 10px;">買い確率</th>
                    <th style="padding: 10px;">売り確率</th>
                    <th style="padding: 10px;">RSI</th>
                    <th style="padding: 10px;">ATR</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """


# --- 4. クオンツ分析データ取得 & 計算エンジン ---
def fetch_forex_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Yahoo Financeから指定した通貨ペアの価格データを取得"""
    ticker_symbol = symbol
    # 方法1: Yahoo Finance Query v8 API 直接取得
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker_symbol)}?range={period}&interval={interval}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            result = res_json.get("chart", {}).get("result", [])[0]
            timestamps = result.get("timestamp", [])
            quote = result.get("indicators", {}).get("quote", [])[0]

            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])

            records = []
            for i in range(len(timestamps)):
                if (
                    i < len(opens) and opens[i] is not None and
                    i < len(highs) and highs[i] is not None and
                    i < len(lows) and lows[i] is not None and
                    i < len(closes) and closes[i] is not None
                ):
                    records.append({
                        "Date": pd.to_datetime(timestamps[i], unit="s"),
                        "Open": float(opens[i]),
                        "High": float(highs[i]),
                        "Low": float(lows[i]),
                        "Close": float(closes[i]),
                        "Volume": 0
                    })

            if records:
                df = pd.DataFrame(records)
                df.set_index("Date", inplace=True)
                df.dropna(inplace=True)
                return df
    except Exception as e:
        logging.warning(f"Direct Yahoo REST API fetch failed for {ticker_symbol}: {e}")

    # 方法2: yfinance ライブラリ
    if YFINANCE_AVAILABLE:
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            df = ticker_obj.history(period=period, interval=interval)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.dropna(inplace=True)
                return df
        except Exception as e:
            logging.error(f"yfinance fetch failed for {ticker_symbol}: {e}")

    return pd.DataFrame()


def generate_technical_features(df: pd.DataFrame, pip_scale: float = 0.01) -> pd.DataFrame:
    """マクロトレンドおよびモメンタム、ボラティリティの技術指標（特徴量）を生成"""
    if df.empty:
        return df

    data = df.copy()

    # 移動平均線
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["SMA_200"] = data["Close"].rolling(window=200).mean()

    # EMA & MACD
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA_12"] - data["EMA_26"]
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]

    # ATR
    high_low = data["High"] - data["Low"]
    high_close = (data["High"] - data["Close"].shift(1)).abs()
    low_close = (data["Low"] - data["Close"].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    data["ATR"] = true_range.rolling(window=14).mean()
    data["ATR_Pips"] = data["ATR"] / pip_scale

    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    data["RSI"] = 100 - (100 / (1 + rs))

    # ボリンジャーバンド
    std_20 = data["Close"].rolling(window=20).std()
    data["Bollinger_Upper"] = data["SMA_20"] + (std_20 * 2)
    data["Bollinger_Lower"] = data["SMA_20"] - (std_20 * 2)

    # 変化率 (Momentum)
    data["Return_1d"] = data["Close"].pct_change(1)
    data["Return_5d"] = data["Close"].pct_change(5)
    data["Return_20d"] = data["Close"].pct_change(20)

    data.dropna(inplace=True)
    return data


def create_target_labels(df: pd.DataFrame, target_pips: float = 250.0, pip_scale: float = 0.01, horizon: int = 15) -> pd.DataFrame:
    """指定したhorizon営業日以内にtarget_pips以上の利益幅に到達するかを判定する教師データを作成"""
    data = df.copy()
    target_val = target_pips * pip_scale

    future_high = data["High"].iloc[::-1].rolling(window=horizon, min_periods=1).max().iloc[::-1].shift(-1)
    future_low = data["Low"].iloc[::-1].rolling(window=horizon, min_periods=1).min().iloc[::-1].shift(-1)

    data["Long_Target_Reached"] = ((future_high - data["Close"]) >= target_val).astype(int)
    data["Short_Target_Reached"] = ((data["Close"] - future_low) >= target_val).astype(int)

    return data


def train_and_predict_probability(
    df: pd.DataFrame,
    target_pips: float = 250.0,
    pip_scale: float = 0.01,
    pair_name: str = "",
    history_df: pd.DataFrame = None
) -> dict:
    """
    RandomForestを用いて、買い(Long)および売り(Short)での目標pips到達確率を予測。
    実績ログ(history_df)が存在する場合は、学習データにフィードバック(再学習・Continual Learning)を反映。
    """
    if len(df) < 60:
        return {"long_prob": 50.0, "short_prob": 50.0, "status": "Insufficient Data"}

    labeled_df = create_target_labels(df, target_pips=target_pips, pip_scale=pip_scale)

    feature_cols = [
        "SMA_5", "SMA_20", "SMA_50", "SMA_200",
        "MACD", "MACD_Signal", "MACD_Hist",
        "ATR_Pips", "RSI", "Bollinger_Upper", "Bollinger_Lower",
        "Return_1d", "Return_5d", "Return_20d"
    ]

    valid_df = labeled_df.dropna(subset=feature_cols + ["Long_Target_Reached", "Short_Target_Reached"])
    if len(valid_df) < 40:
        return {"long_prob": 50.0, "short_prob": 50.0, "status": "Insufficient Valid Rows"}

    X = valid_df[feature_cols].copy()
    y_long = valid_df["Long_Target_Reached"].copy()
    y_short = valid_df["Short_Target_Reached"].copy()

    # --- 継続学習 (Continual Learning): 過去の確定済み予測ログからのフィードバック反映 ---
    sample_weights_long = np.ones(len(X))
    sample_weights_short = np.ones(len(X))

    if history_df is not None and not history_df.empty and pair_name:
        # 当該通貨ペアの確定済み予測ログ (outcome == 1 or 0) を取得
        pair_logs = history_df[(history_df["pair_name"] == pair_name) & (history_df["outcome"].isin([0, 1]))]
        if not pair_logs.empty:
            for _, log in pair_logs.iterrows():
                log_time = pd.to_datetime(log["timestamp"])
                outcome = int(log["outcome"])
                pred_dir = str(log["pred_direction"])

                # 直近の日付で最も近い特徴量行を探す
                time_diffs = (valid_df.index - log_time).abs()
                if not time_diffs.empty and time_diffs.min() < pd.Timedelta(days=5):
                    nearest_idx = time_diffs.idxmin()
                    row_pos = valid_df.index.get_loc(nearest_idx)

                    # 確定済みの勝ち(1)なら重みを強化、負け(0)なら該当方向のラベル調整
                    if pred_dir == "Long":
                        y_long.iloc[row_pos] = outcome
                        sample_weights_long[row_pos] += 2.0 # フィードバック重み強化
                    elif pred_dir == "Short":
                        y_short.iloc[row_pos] = outcome
                        sample_weights_short[row_pos] += 2.0

    # RandomForest (Long)
    rf_long = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_long.fit(X, y_long, sample_weight=sample_weights_long)

    latest_features = X.iloc[[-1]]

    # 買い確率の安全取得（IndexError防止）
    long_probs = rf_long.predict_proba(latest_features)[0]
    long_prob_raw = long_probs[1] if len(long_probs) > 1 else (1.0 if y_long.iloc[-1] == 1 else 0.0)

    # RandomForest (Short)
    rf_short = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_short.fit(X, y_short, sample_weight=sample_weights_short)

    short_probs = rf_short.predict_proba(latest_features)[0]
    short_prob_raw = short_probs[1] if len(short_probs) > 1 else (1.0 if y_short.iloc[-1] == 1 else 0.0)

    long_prob = round(float(long_prob_raw * 100), 1)
    short_prob = round(float(short_prob_raw * 100), 1)

    return {
        "long_prob": long_prob,
        "short_prob": short_prob,
        "status": "Success",
        "latest_close": float(df["Close"].iloc[-1]),
        "latest_rsi": float(df["RSI"].iloc[-1]) if "RSI" in df.columns else 50.0,
        "latest_atr_pips": float(df["ATR_Pips"].iloc[-1]) if "ATR_Pips" in df.columns else 0.0
    }


def analyze_all_gmo_pairs(period: str = "1y", target_pips: float = 250.0, history_df: pd.DataFrame = None) -> list:
    """全10通貨ペアのデータを一括で取得・分析"""
    results = []
    for pair in SBI_PAIRS:
        df = fetch_forex_data(pair["symbol"], period=period)
        if not df.empty:
            df = generate_technical_features(df, pip_scale=pair["pip_scale"])
            pred = train_and_predict_probability(
                df,
                target_pips=target_pips,
                pip_scale=
