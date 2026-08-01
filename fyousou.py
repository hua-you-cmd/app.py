# ==========================================
# FILE: fyousou.py
# ==========================================

"""
GMO / SBI FX クオンツAI予測ダッシュボード (fyousou.py - 完全独立スタンドアロン版)
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
                pip_scale=pair["pip_scale"],
                pair_name=pair["name"],
                history_df=history_df
            )
            latest_price = df["Close"].iloc[-1]
            results.append({
                "name": pair["name"],
                "display_name": pair["disp"],
                "symbol": pair["symbol"],
                "price": round(float(latest_price), 4),
                "long_prob": pred["long_prob"],
                "short_prob": pred["short_prob"],
                "rsi": round(pred.get("latest_rsi", 50.0), 1),
                "atr_pips": round(pred.get("latest_atr_pips", 0.0), 1),
                "data": df
            })
    return results


# --- 5. STREAMLIT UI ---
st.set_page_config(page_title="GMO / SBI FX AI Quant Predictor", layout="wide", page_icon="📈")

st.title("📈 SBI / GMO FX AI クオンツ到達確率予測システム")
st.caption("Yahoo Finance 100%リアルタイムデータ ＆ RandomForest機械学習モデル ＆ 実績学習トラッカー (単一完全独立スクリプト - fyousou.py)")

# サイドバー: パスコード保護 (文字は伏字 masked, パスワード番号の生テキスト表示なし)
st.sidebar.title("🔐 アクセス認証")
passcode = st.sidebar.text_input("パスコードを入力してください", type="password", placeholder="••••")
if passcode != "5689":
    st.sidebar.warning("正しいパスコードを入力してください。")
    st.stop()

st.sidebar.success("🔑 認証成功")

# サイドバー設定
st.sidebar.markdown("---")
st.sidebar.title("⚙️ 分析パラメータ設定")
target_pips_setting = st.sidebar.slider("目標到達pips (例: 250pips)", min_value=50, max_value=500, value=250, step=10)

st.sidebar.markdown("---")
st.sidebar.title("📧 メール自動通知設定")
enable_email = st.sidebar.checkbox("メール通知を有効化", value=False)
smtp_server = st.sidebar.text_input("SMTPサーバー", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTPポート", value=587)
sender_email = st.sidebar.text_input("送信元Email", value="")
sender_password = st.sidebar.text_input("Appパスワード", type="password", value="")
receiver_email = st.sidebar.text_input("送信先Email", value="huashenfo@gmail.com")

# 既存の過去ログ読み込み
history_df_raw = load_prediction_history()

with st.spinner("Yahoo Financeからリアルタイムデータを取得 ＆ フィードバック再学習中..."):
    results = analyze_all_gmo_pairs(target_pips=target_pips_setting, history_df=history_df_raw)
    pairs_map = {r["name"]: r["data"] for r in results if "data" in r and not r["data"].empty}
    
    # 自動答え合わせ(Outcome Evaluation)実行
    history_df = evaluate_prediction_outcomes(pairs_map)

# UIレイアウト (タブ構造)
tab1, tab2, tab3 = st.tabs(["📊 リアルタイム到達確率一覧 & チャート", "📈 AI予測精度トラッカー & 勝率検証", "📧 メール通知設定"])

with tab1:
    if results:
        results_df_for_email = pd.DataFrame(results)

        # メール送信ボタン
        if enable_email and sender_email and sender_password and receiver_email:
            if st.sidebar.button("📨 分析レポートをメール送信", type="primary"):
                html_body = build_signal_email_html(results_df_for_email)
                success = send_smtp_email(
                    smtp_server, int(smtp_port), sender_email, sender_password, receiver_email,
                    f"📈【FX AI Quant Report】10通貨ペア到達確率レポート ({datetime.now().strftime('%m/%d %H:%M')})",
                    html_body
                )
                if success:
                    st.sidebar.success(f"✅ {receiver_email} へメールを送信しました！")
                else:
                    st.sidebar.error("❌ メール送信に失敗しました。設定をご確認ください。")

        col_head1, col_head2 = st.columns([3, 1])
        with col_head1:
            st.subheader(f"📊 主要10通貨ペア {target_pips_setting}pips 到達確率一覧")
        with col_head2:
            if st.button("📌 現在の予測結果を履歴ログに自動記録", type="primary"):
                recorded_cnt = record_current_predictions(results, target_pips_setting)
                st.success(f"✅ {recorded_cnt} 件の予測ログを記録しました！")

        df_summary = pd.DataFrame([
            {
                "通貨ペア": r["name"],
                "名称": r["display_name"],
                "現在値": r["price"],
                "買い到達確率 (%)": f"{r['long_prob']}%",
                "売り到達確率 (%)": f"{r['short_prob']}%",
                "RSI (14日)": r["rsi"],
                "ATR (Pips)": r["atr_pips"]
            }
            for r in results
        ])
        st.dataframe(df_summary, use_container_width=True)

        # グラフ表示
        selected_pair_name = st.selectbox("分析チャート表示通貨ペアを選択:", [r["name"] for r in results])
        selected_res = next((r for r in results if r["name"] == selected_pair_name), None)

        if selected_res and not selected_res["data"].empty:
            df_chart = selected_res["data"]
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'],
                high=df_chart['High'],
                low=df_chart['Low'],
                close=df_chart['Close'],
                name='OHLC'
            ))
            if 'SMA_20' in df_chart.columns:
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA_20'], mode='lines', name='SMA 20'))
            if 'Bollinger_Upper' in df_chart.columns:
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Bollinger_Upper'], mode='lines', name='Bollinger Upper', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Bollinger_Lower'], mode='lines', name='Bollinger Lower', line=dict(dash='dash')))

            fig.update_layout(title=f"{selected_pair_name} チャート & テクニカル分析", xaxis_title="日付", yaxis_title="価格")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📈 AI予測精度トラッカー (Prediction Tracker & Outcome Evaluator)")
    st.caption("予測結果と実際の価格変動のズレ（正解/不正解）を自動追跡し、RandomForestモデルへ継続的に学習フィードバックを行います。")

    hist_data = load_prediction_history()

    if hist_data.empty:
        st.info("💡 まだ予測履歴が記録されていません。タブ1の『📌 現在の予測結果を履歴ログに自動記録』ボタンを押してログを記録してください。")
    else:
        # メトリクス計算
        total_preds = len(hist_data)
        evaluated_df = hist_data[hist_data["outcome"].isin([0, 1])]
        total_eval = len(evaluated_df)
        wins = len(evaluated_df[evaluated_df["outcome"] == 1])
        losses = len(evaluated_df[evaluated_df["outcome"] == 0])

        overall_win_rate = round((wins / total_eval * 100), 1) if total_eval > 0 else 0.0

        # 直近10件的中率
        recent_10 = evaluated_df.tail(10)
        recent_wins = len(recent_10[recent_10["outcome"] == 1])
        recent_win_rate = round((recent_wins / len(recent_10) * 100), 1) if len(recent_10) > 0 else 0.0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("累計予測回数", f"{total_preds} 件")
        col_m2.metric("確定勝負数", f"{total_eval} 件", f"判定中: {total_preds - total_eval} 件")
        col_m3.metric("通算勝率", f"{overall_win_rate} %", f"勝ち: {wins} / 負け: {losses}")
        col_m4.metric("直近10件的中率", f"{recent_win_rate} %", f"直近勝ち: {recent_wins} 件")

        st.markdown("---")

        # 勝率推移チャート
        if not evaluated_df.empty:
            st.markdown("### 📊 累積勝率推移グラフ")
            evaluated_df = evaluated_df.copy()
            evaluated_df["cum_wins"] = (evaluated_df["outcome"] == 1).cumsum()
            evaluated_df["cum_total"] = np.arange(1, len(evaluated_df) + 1)
            evaluated_df["cum_win_rate"] = (evaluated_df["cum_wins"] / evaluated_df["cum_total"]) * 100

            fig_win = go.Figure()
            fig_win.add_trace(go.Scatter(
                x=evaluated_df["timestamp"],
                y=evaluated_df["cum_win_rate"],
                mode="lines+markers",
                name="累積勝率 (%)",
                line=dict(color="#16a34a", width=3)
            ))
            fig_win.update_layout(
                title="予測精度・勝率の推移 (%)",
                xaxis_title="予測日時",
                yaxis_title="勝率 (%)",
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_win, use_container_width=True)

        st.markdown("### 📄 予測履歴・答え合わせ一覧ログ")
        st.dataframe(hist_data, use_container_width=True)

with tab3:
    st.subheader("📧 メール通知設定 & システム情報")
    st.info(f"現在の送信先設定: {receiver_email}")
    st.caption("サイドバーの『メール通知を有効化』をチェックし、Gmail Appパスワードを入力するとレポートが届きます。")

st.markdown("---")
st.caption("© 2026 GMO FX AI Quant System | fyousou.py")


# ==========================================
# FILE: app.py
# ==========================================

"""
GMO FX AI Quant Analysis - Streamlit Web Application
(100% 独立・完全動作 Python/Streamlit ダッシュボード)
【新機能】予測精度トラッカー (Prediction Tracker)、自動答え合わせ (Outcome Evaluator)、勝率可視化 & フィードバック継続学習
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 自作モジュールのインポート
from model import (
    GMO_PAIRS,
    analyze_all_gmo_pairs,
    fetch_forex_data,
    generate_technical_features,
    load_prediction_history,
    record_current_predictions_model,
    evaluate_prediction_outcomes
)
from notifier import build_signal_email_html, send_smtp_email

# 1. ページ基本設定
st.set_page_config(
    page_title="GMO FX AI Quant - 200〜300pips到達確率判定システム",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: bold; }
    .metric-card {
        background-color: #1e293b;
        border: 2px solid #334155;
        border-radius: 6px;
        padding: 16px;
        text-align: center;
    }
    .status-highlight {
        color: #10b981;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# 2. パスワード保護ゲート (パスワード: 5689)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 GMO FX AI Quant - パスワード保護ゲート")
    st.caption("本システムは保護されています。パスコードを入力してログインしてください。")

    col_lock1, col_lock2 = st.columns([2, 1])
    with col_lock1:
        passcode_input = st.text_input("パスコードを入力:", type="password", placeholder="••••")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("パスコードを自動入力"):
                st.session_state.authenticated = True
                st.rerun()
        with col_btn2:
            if st.button("ログイン (Unlock)", type="primary"):
                if passcode_input == "5689":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ パスコードが正しくありません")
    st.stop()


# 3. セッション状態の初期化
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None


# 4. ヘルパー関数: 分析実行
def run_analysis(target_pips: int):
    with st.spinner("Yahoo Financeから最新データを取得し、AIモデル(継続学習適用)で確率を計算中..."):
        # 既存予測ログのロード
        hist_df = load_prediction_history()

        # 分析 & 継続学習実行
        df_results = analyze_all_gmo_pairs(target_pips=target_pips, history_df=hist_df)
        st.session_state.analysis_results = df_results
        st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 最新データに基づき自動答え合わせ (Outcome Evaluation) をバックグラウンド処理
        pairs_map = {}
        for pair_name, cfg in GMO_PAIRS.items():
            raw_data = fetch_forex_data(cfg["ticker"], period="1y", interval="1d")
            if not raw_data.empty:
                pairs_map[pair_name] = generate_technical_features(raw_data, pip_scale=cfg["pip_scale"])
        evaluate_prediction_outcomes(pairs_map)


# 5. ヘルパー関数: Gemini AI マクロ分析
def generate_gemini_analysis_python(pair_name: str, current_price: float, prob: float, trend: str, target_pips: int, api_key: str = None) -> str:
    key = api_key or os.getenv("GEMINI_API_KEY", "")

    prompt = (
        f"あなたはプロのFXクオンツアナリストおよび為替ストラテジストです。\n"
        f"以下の通貨ペアデータに基づき、プロ投資家向けのマクロ分析とテクニカル解説を作成してください。\n\n"
        f"・通貨ペア: {pair_name}\n"
        f"・現在レート: {current_price}\n"
        f"・AIモデルによる{target_pips}pips到達確率: {prob}%\n"
        f"・大局トレンド: {trend}\n\n"
        f"【出力構成】\n"
        f"1. 📊 マクロ環境と金利差動向 (日米欧中央銀行の方針と為替への影響)\n"
        f"2. 📈 テクニカル重要レジスタンス & サポートライン\n"
        f"3. 🎯 200〜300pips狙いの最適なエントリー・損切り(SL)・利確(TP)戦略\n"
        f"4. ⚠️ 注意すべき経済指標発表リスク\n"
    )

    if not key:
        return (
            f"### 📊 {pair_name} クオンツAI分析レポート ({target_pips}pips到達確率: {prob}%)\n\n"
            f"**1. マクロ経済環境 & 金利差シナリオ**\n"
            f"- 大局トレンド判定: **{trend}**\n"
            f"- 主要中央銀行（FRB・日銀・ECB）の政策金利スタンス乖離が長期トレンドを形成しています。\n"
            f"- AIランダムフォレストモデルによる評価確率 **{prob}%** は、直近のATRボラティリティと移動平均線（200SMA）乖離率から算出された高期待値シグナルです。\n\n"
            f"**2. テクニカル重要水準 & リスク管理**\n"
            f"- **推奨方向**: {trend} に沿った順張りエントリー\n"
            f"- **目標利確幅 (TP)**: 現在値 ({current_price}) から ±{target_pips} pips\n"
            f"- **推奨損切り (SL)**: 直近高値・安値の外側 (ATRの1.5倍を目安に設定)\n\n"
            f"*(注: サイドバーで Gemini API Key を設定すると、リアルタイムGemini AI解説が有効になります)*"
        )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "解説を生成できませんでした。")
    except Exception as e:
        return f"⚠️ Gemini APIエラー: {e}\n\n標準スコア分析:\n・通貨ペア: {pair_name}\n・AI到達確率: {prob}%\n・トレンド: {trend}"

    return "分析データを取得できませんでした。"


# 6. サイドバー UI
st.sidebar.title("⚙️ GMO FX AI Quant 設定")

st.sidebar.markdown("### 1. 分析パラメータ")
target_pips_setting = st.sidebar.slider("目標利益幅 (pips)", min_value=150, max_value=400, value=250, step=10, help="200~300pips (2.0~3.0円) を推奨")
alert_threshold = st.sidebar.slider("通知対象AI確率 (%)", min_value=50, max_value=90, value=65, step=5)

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Gemini AI Key (任意)")
gemini_api_key_input = st.sidebar.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. メール自動通知設定")
enable_email = st.sidebar.checkbox("シグナルメール通知を有効化", value=False)
smtp_server = st.sidebar.text_input("SMTP サーバー", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP ポート", value=587)
sender_email = st.sidebar.text_input("送信元 Email", value="")
sender_password = st.sidebar.text_input("App パスワード", type="password", value="")
receiver_email = st.sidebar.text_input("送信先 Email", value="huashenfo@gmail.com")

if st.sidebar.button("🔒 再ロック (ログアウト)"):
    st.session_state.authenticated = False
    st.rerun()


# 7. メインヘッダー
col_title, col_btn = st.columns([3, 1])

with col_title:
    st.title("🤖 GMO FX AI Quant - 200〜300pips到達確率モニター")
    st.caption("GMO為替10銘柄に対応。実績答え合わせ(Prediction Tracker) & 機械学習フィードバック継続学習機能を完備。")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 最新データ再計算", type="primary"):
        run_analysis(target_pips_setting)


# 初期データ実行
if st.session_state.analysis_results is None:
    run_analysis(target_pips_setting)

df_res = st.session_state.analysis_results
last_time = st.session_state.last_updated

st.info(f"🕒 最終データ更新日時: **{last_time}** (Yahoo Finance リアルタイムデータ & AIモデルフィードバック反映)")


# 8. ハイライト KPI カード
if df_res is not None and not df_res.empty:
    top_pair = df_res.iloc[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="🏆 最優先エントリー推奨", value=top_pair["通貨ペア"])
    with kpi2:
        st.metric(label="🎯 200〜300pips成功確率", value=f"{top_pair['AI成功確率 (%)']}%")
    with kpi3:
        st.metric(label="📍 推奨アクション", value=top_pair["推奨タイミング"])
    with kpi4:
        st.metric(label="📊 大局トレンド", value=top_pair["大局トレンド"].split("(")[0])

    st.markdown("---")

    # 9. タブUI
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 確率ランキング MATRIX",
        "📈 AI予測精度トラッカー & 勝率検証",
        "📈 詳細テクニカルチャート",
        "✨ Gemini AI マクロ解説",
        "📋 全ソースコード一括表示/コピー"
    ])

    # TAB 1: Ranking Table
    with tab1:
        col_t1_head, col_t1_btn = st.columns([3, 1])
        with col_t1_head:
            st.subheader("GMO為替 10銘柄 確率ランキング")
        with col_t1_btn:
            if st.button("📌 現在の予測を履歴ログに自動記録", type="primary"):
                cnt = record_current_predictions_model(df_res, target_pips_setting)
                st.success(f"✅ {cnt} 件の予測結果を履歴ログに保存しました！")

        def style_prob(val):
            if val >= 70:
                return "background-color: #064e3b; color: #34d399; font-weight: bold;"
            elif val >= 60:
                return "background-color: #1e3a8a; color: #93c5fd;"
            return ""

        styled_df = df_res.style.applymap(style_prob, subset=["AI成功確率 (%)"])
        st.dataframe(styled_df, use_container_width=True, height=400)

        # メール送信機能
        if enable_email and sender_email and sender_password and receiver_email:
            high_signals = df_res[df_res["AI成功確率 (%)"] >= alert_threshold]
            if not high_signals.empty:
                st.success(f"📧 確率 {alert_threshold}% 以上のシグナルが点灯中です！")
                if st.button("📨 アラートメールを送信"):
                    email_body = build_signal_email_html(df_res, threshold_pct=alert_threshold)
                    sent = send_smtp_email(
                        smtp_server, int(smtp_port), sender_email, sender_password, receiver_email,
                        f"🚨【FX AI Alert】高確率シグナル点灯 ({high_signals.iloc[0]['通貨ペア']} {high_signals.iloc[0]['AI成功確率 (%)']}%)",
                        email_body
                    )
                    if sent:
                        st.balloons()
                        st.success("シグナル通知メールを送信しました！")

    # TAB 2: AI Prediction Tracker & Evaluator
    with tab2:
        st.subheader("📈 AI予測精度トラッカー (Prediction Tracker & Outcome Evaluator)")
        st.caption("予測結果と実際の価格変動のズレ（正解/不正解）を自動追跡し、RandomForestモデルへ継続的に学習フィードバックを行います。")

        hist_data = load_prediction_history()

        if hist_data.empty:
            st.info("💡 まだ予測履歴が記録されていません。タブ1の『📌 現在の予測を履歴ログに自動記録』ボタンを押してログを記録してください。")
        else:
            total_preds = len(hist_data)
            evaluated_df = hist_data[hist_data["outcome"].isin([0, 1])]
            total_eval = len(evaluated_df)
            wins = len(evaluated_df[evaluated_df["outcome"] == 1])
            losses = len(evaluated_df[evaluated_df["outcome"] == 0])

            overall_win_rate = round((wins / total_eval * 100), 1) if total_eval > 0 else 0.0

            recent_10 = evaluated_df.tail(10)
            recent_wins = len(recent_10[recent_10["outcome"] == 1])
            recent_win_rate = round((recent_wins / len(recent_10) * 100), 1) if len(recent_10) > 0 else 0.0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("累計予測回数", f"{total_preds} 件")
            m2.metric("確定勝負数", f"{total_eval} 件", f"判定中: {total_preds - total_eval} 件")
            m3.metric("通算勝率", f"{overall_win_rate} %", f"勝ち: {wins} / 負け: {losses}")
            m4.metric("直近10件的中率", f"{recent_win_rate} %", f"直近勝ち: {recent_wins} 件")

            st.markdown("---")

            if not evaluated_df.empty:
                st.markdown("### 📊 累積勝率推移グラフ")
                evaluated_df = evaluated_df.copy()
                evaluated_df["cum_wins"] = (evaluated_df["outcome"] == 1).cumsum()
                evaluated_df["cum_total"] = np.arange(1, len(evaluated_df) + 1)
                evaluated_df["cum_win_rate"] = (evaluated_df["cum_wins"] / evaluated_df["cum_total"]) * 100

                fig_win = go.Figure()
                fig_win.add_trace(go.Scatter(
                    x=evaluated_df["timestamp"],
                    y=evaluated_df["cum_win_rate"],
                    mode="lines+markers",
                    name="累積勝率 (%)",
                    line=dict(color="#10b981", width=3)
                ))
                fig_win.update_layout(
                    title="予測精度・勝率の推移 (%)",
                    xaxis_title="予測日時",
                    yaxis_title="勝率 (%)",
                    template="plotly_dark",
                    yaxis=dict(range=[0, 100])
                )
                st.plotly_chart(fig_win, use_container_width=True)

            st.markdown("### 📄 予測履歴・答え合わせ一覧ログ")
            st.dataframe(hist_data, use_container_width=True)

    # TAB 3: Detailed Technical Charts
    with tab3:
        st.subheader("テクニカル指標 & チャート詳細分析")
        selected_pair = st.selectbox("分析する通貨ペアを選択:", list(GMO_PAIRS.keys()))

        pair_info = GMO_PAIRS[selected_pair]
        raw_df = fetch_forex_data(pair_info["ticker"], period="1y", interval="1d")

        if not raw_df.empty and len(raw_df) > 30:
            feat_df = generate_technical_features(raw_df, pip_scale=pair_info["pip_scale"])

            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f"{selected_pair} 日足 & 移動平均線 (SMA20/50/200)", "MACD (12, 26, 9)", "ATR (14日) ボラティリティ (pips)")
            )

            fig.add_trace(go.Candlestick(
                x=feat_df.index,
                open=feat_df["Open"], high=feat_df["High"],
                low=feat_df["Low"], close=feat_df["Close"],
                name="ローソク足"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["SMA_20"], line=dict(color="#f59e0b", width=1.5), name="SMA 20"), row=1, col=1)
            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["SMA_50"], line=dict(color="#3b82f6", width=1.5), name="SMA 50"), row=1, col=1)
            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["SMA_200"], line=dict(color="#ef4444", width=2), name="SMA 200"), row=1, col=1)

            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["MACD"], line=dict(color="#3b82f6"), name="MACD"), row=2, col=1)
            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["MACD_Signal"], line=dict(color="#f97316"), name="Signal"), row=2, col=1)
            fig.add_trace(go.Bar(x=feat_df.index, y=feat_df["MACD_Hist"], name="Histogram", marker_color="#10b981"), row=2, col=1)

            fig.add_trace(go.Scatter(x=feat_df.index, y=feat_df["ATR_Pips"], line=dict(color="#8b5cf6", width=2), name="ATR (pips)"), row=3, col=1)

            fig.update_layout(height=750, template="plotly_dark", showlegend=True, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

    # TAB 4: Gemini AI Macro Insight
    with tab4:
        st.subheader("Gemini AI によるマクロ環境 & トレンド解説")
        pair_ai_select = st.selectbox("AI分析レポート生成通貨ペア:", list(GMO_PAIRS.keys()), key="ai_pair_select")

        row_match = df_res[df_res["通貨ペア"] == pair_ai_select]
        if not row_match.empty:
            cur_p = float(row_match.iloc[0]["現在値"])
            cur_prob = float(row_match.iloc[0]["AI成功確率 (%)"])
            cur_trend = str(row_match.iloc[0]["大局トレンド"])

            if st.button("✨ Gemini AI マクロレポートを生成", type="primary"):
                with st.spinner("Gemini AIがマクロ指標とテクニカルラインを解析中..."):
                    ai_report = generate_gemini_analysis_python(
                        pair_ai_select, cur_p, cur_prob, cur_trend, target_pips_setting, gemini_api_key_input
                    )
                    st.markdown(ai_report)

    # TAB 5: Python Full Code Exporter (Pythonコード専用コピー & ダウンロード)
    with tab5:
        st.subheader("🐍 Python専用 ソースコード完全取得 & 分割コピー")
        st.info("💡 **「コードが途中で切れて半分しかコピーできない」場合**: 画面上部の【📥 ファイル直接保存 (.py)】でファイルとして保存するか、以下の【✂️ Part 1 (前半)】と【✂️ Part 2 (後半)】に分かれた分割ボックス、またはファイル毎の個別ボックスをご利用ください！")

        # 1. fyousou.py 単一完全独立ファイル
        if os.path.exists("fyousou.py"):
            with open("fyousou.py", "r", encoding="utf-8") as f:
                fyousou_code = f.read()
            st.markdown("### ⚡ 1. fyousou.py (1本で完全動作する単一独立スクリプト)")
            st.success("💡 他のファイルが不要で、この1ファイルのみで全AI分析・予測トラッカー・ダッシュボードが100%動作します！")
            
            c_dl1, c_info1 = st.columns([1, 2])
            with c_dl1:
                st.download_button(
                    label="📥 fyousou.py を直接ダウンロード (.py)",
                    data=fyousou_code,
                    file_name="fyousou.py",
                    mime="text/x-python",
                    type="primary",
                    use_container_width=True
                )
            with c_info1:
                st.caption(f"全 {len(fyousou_code.splitlines())} 行 / 行数制限なしで100%完結")

            st.text_area("fyousou.py 全ソースコード (枠内クリック → Ctrl+A全選択 → Ctrl+Cコピー):", value=fyousou_code, height=350, key="ta_fyousou_main")

        st.markdown("---")

        # Pythonコード専用束 (fyousou.py + app.py + model.py + notifier.py)
        python_files = [
            ("fyousou.py (単一独立スクリプト)", "fyousou.py"),
            ("app.py (Streamlit Webアプリメイン)", "app.py"),
            ("model.py (クオンツ分析 & Yahoo Financeデータ取得)", "model.py"),
            ("notifier.py (SMTPメール自動通知)", "notifier.py")
        ]

        python_code_text = ""
        for label, filepath in python_files:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    python_code_text += f"# ==========================================\n# FILE: {filepath}\n# ({label})\n# ==========================================\n\n{content}\n\n"

        lines_all = python_code_text.splitlines()
        mid_idx = len(lines_all) // 2
        part1_text = "\n".join(lines_all[:mid_idx])
        part2_text = "\n".join(lines_all[mid_idx:])

        st.markdown("### ✂️ 2. Python全コード【分割コピー用】 (Part 1 / Part 2)")
        st.caption("長大コードによるブラウザクリップボードの切り捨て事故を完全に防ぎます。")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### 🅰️ Part 1 (前半部分)")
            st.download_button(
                label="📥 Part 1 をダウンロード (.py)",
                data=part1_text,
                file_name="all_python_part1.py",
                mime="text/x-python",
                key="dl_p1"
            )
            st.text_area("Part 1 (前半コード - Ctrl+A → Ctrl+C):", value=part1_text, height=350, key="ta_part1")

        with col_p2:
            st.markdown("#### 🅱️ Part 2 (後半部分)")
            st.download_button(
                label="📥 Part 2 をダウンロード (.py)",
                data=part2_text,
                file_name="all_python_part2.py",
                mime="text/x-python",
                key="dl_p2"
            )
            st.text_area("Part 2 (後半コード - Ctrl+A → Ctrl+C):", value=part2_text, height=350, key="ta_part2")

        st.markdown("---")

        st.markdown("### 📦 3. Python全ファイル一括ダウンロード & 結合コード")
        st.download_button(
            label="📥 Python全コード一括ファイルをダウンロード (all_python_code.py)",
            data=python_code_text,
            file_name="all_python_code.py",
            mime="text/x-python",
            type="primary",
            key="dl_all_py"
        )
        st.text_area("Python全コード一括テキスト (Ctrl+A -> Ctrl+C):", value=python_code_text, height=400, key="ta_all_py")

        st.markdown("---")
        st.markdown("### 📄 4. Pythonファイル別 個別コピー & ダウンロード")
        for label, filepath in python_files:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    file_code = f.read()
                with st.expander(f"📄 {filepath} — {label}", expanded=True):
                    st.download_button(
                        label=f"📥 {filepath} を直接ダウンロード",
                        data=file_code,
                        file_name=filepath,
                        mime="text/x-python",
                        key=f"dl_indiv_{filepath}"
                    )
                    st.text_area(f"{filepath} コード全 {len(file_code.splitlines())} 行:", value=file_code, height=300, key=f"ta_indiv_{filepath}")

st.markdown("---")
st.caption("© 2026 GMO FX AI Quant System | Passcode: 5689 | Powered by Python & Streamlit")


# ==========================================
# FILE: model.py
# ==========================================

"""
GMO FX AI Quant Analysis - ML Model & Feature Engineering Module
(データ取得、特徴量生成、機械学習モデル学習、200〜300pips到達確率算出バックエンド)
【新機能】予測ログ蓄積 (Prediction Tracker)、自動答え合わせ (Outcome Evaluator)、フィードバック継続学習 (Continual Learning)
"""

import os
import json
import logging
import math
import urllib.request
import urllib.parse
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. SBI / GMO為替メインレート 10通貨ペアの定義と設定
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

# エイリアス設定
TARGET_PAIRS = SBI_PAIRS
GMO_PAIRS = {pair["name"]: pair for pair in SBI_PAIRS}
HISTORY_FILE = "prediction_history.csv"


# --- 予測ログ管理 & 答え合わせ (Outcome Evaluator) ---
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


def record_current_predictions_model(results_df: pd.DataFrame, target_pips: float):
    """現在の予測結果をログに保存"""
    df_hist = load_prediction_history()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_rows = []

    for idx, row in results_df.iterrows():
        pair_name = row.get("通貨ペア", "")
        price = row.get("現在値", 0.0)
        success_prob = row.get("AI成功確率 (%)", 50.0)

        # ドル・円ペアでの方向性
        trend = row.get("大局トレンド", "")
        pred_dir = "Long" if "上昇" in trend or "BULL" in trend else "Short" if "下降" in trend or "BEAR" in trend else "Long"

        # スキップ判定
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
            "long_prob": success_prob if pred_dir == "Long" else round(100.0 - success_prob, 1),
            "short_prob": success_prob if pred_dir == "Short" else round(100.0 - success_prob, 1),
            "outcome": -1,
            "evaluated_at": ""
        })

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_updated = pd.concat([df_hist, df_new], ignore_index=True)
        save_prediction_history(df_updated)
        return len(new_rows)
    return 0


def evaluate_prediction_outcomes(pairs_data_map: dict) -> pd.DataFrame:
    """過去の未確定予測ログに対し、実際の最新チャートデータから答え合わせ（正解判定）を行う。"""
    df_hist = load_prediction_history()
    if df_hist.empty:
        return df_hist

    updated = False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for idx, row in df_hist.iterrows():
        if row["outcome"] != -1 and not pd.isna(row["outcome"]):
            continue

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


def fetch_forex_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Yahoo Financeから指定した通貨ペアの価格データを取得"""
    ticker_symbol = symbol

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
    """技術指標（特徴量）を生成"""
    if df.empty:
        return df

    data = df.copy()

    # SMA
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
    data["BB_Upper"] = data["SMA_20"] + (std_20 * 2)
    data["BB_Lower"] = data["SMA_20"] - (std_20 * 2)
    data["BB_Width"] = (data["BB_Upper"] - data["BB_Lower"]) / data["SMA_20"]

    # トレンド乖離率・マクロ特徴量
    data["Dist_SMA200"] = (data["Close"] - data["SMA_200"]) / data["SMA_200"]
    data["Dist_SMA50"] = (data["Close"] - data["SMA_50"]) / data["SMA_50"]
    data["Return_5D"] = data["Close"].pct_change(5)
    data["Return_20D"] = data["Close"].pct_change(20)

    # トレンド方向
    data["Trend_State"] = 0
    data.loc[(data["Close"] > data["SMA_50"]) & (data["SMA_50"] > data["SMA_200"]), "Trend_State"] = 1
    data.loc[(data["Close"] < data["SMA_50"]) & (data["SMA_50"] < data["SMA_200"]), "Trend_State"] = -1

    return data.dropna()


def create_target_label(df: pd.DataFrame, pip_scale: float, target_pips: float = 250, forward_days: int = 10) -> pd.Series:
    """正解ラベル作成"""
    target_distance = target_pips * pip_scale

    future_high_max = df["High"].iloc[::-1].rolling(window=forward_days).max().iloc[::-1]
    future_low_min = df["Low"].iloc[::-1].rolling(window=forward_days).min().iloc[::-1]

    long_profit = (future_high_max - df["Close"]) >= target_distance
    short_profit = (df["Close"] - future_low_min) >= target_distance

    target = np.where(
        (df["Trend_State"] == 1) & long_profit, 1,
        np.where((df["Trend_State"] == -1) & short_profit, 1, 0)
    )

    return pd.Series(target, index=df.index)


def train_and_predict_probability(
    df: pd.DataFrame,
    pip_scale: float,
    target_pips: float = 250,
    pair_name: str = "",
    history_df: pd.DataFrame = None
) -> dict:
    """
    Random Forest機械学習モデルを学習させ、現在足における「200〜300pips獲得成功確率」を計算します。
    フィードバック継続学習 (Continual Learning) に対応。
    """
    feature_cols = [
        "MACD", "MACD_Hist", "RSI", "ATR_Pips", "BB_Width",
        "Dist_SMA200", "Dist_SMA50", "Return_5D", "Return_20D", "Trend_State"
    ]

    target = create_target_label(df, pip_scale, target_pips=target_pips)
    data = df.copy()
    data["Target"] = target

    clean_data = data.dropna(subset=feature_cols + ["Target"])
    train_df = clean_data.iloc[:-10]

    if len(train_df) < 50:
        return {
            "current_price": float(df["Close"].iloc[-1]),
            "success_probability": 50.0,
            "trend_label": "データ不足",
            "entry_recommendation": "待機",
            "atr_pips": 0.0,
            "rsi": 50.0,
            "target_pips": target_pips,
            "target_price_delta": target_pips * pip_scale,
            "feature_importance": {}
        }

    X_train = train_df[feature_cols].copy()
    y_train = train_df["Target"].copy()
    sample_weights = np.ones(len(X_train))

    # フィードバック重み付け (Continual Learning)
    if history_df is not None and not history_df.empty and pair_name:
        pair_logs = history_df[(history_df["pair_name"] == pair_name) & (history_df["outcome"].isin([0, 1]))]
        if not pair_logs.empty:
            for _, log in pair_logs.iterrows():
                log_time = pd.to_datetime(log["timestamp"])
                outcome = int(log["outcome"])
                time_diffs = (train_df.index - log_time).abs()
                if not time_diffs.empty and time_diffs.min() < pd.Timedelta(days=5):
                    nearest_idx = time_diffs.idxmin()
                    row_pos = train_df.index.get_loc(nearest_idx)
                    y_train.iloc[row_pos] = outcome
                    sample_weights[row_pos] += 2.0

    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train, sample_weight=sample_weights)

    latest_features = df[feature_cols].iloc[[-1]]
    probs = model.predict_proba(latest_features)[0]
    prob_class1 = probs[1] if len(probs) > 1 else (1.0 if y_train.iloc[-1] == 1 else 0.0)
    prob_percent = round(float(prob_class1 * 100), 1)

    importances = dict(zip(feature_cols, [round(float(v), 3) for v in model.feature_importances_]))

    latest_row = df.iloc[-1]
    close_price = float(latest_row["Close"])
    atr_pips = round(float(latest_row["ATR_Pips"]), 1)
    trend_state = int(latest_row["Trend_State"])
    rsi = round(float(latest_row["RSI"]), 1)
    macd_hist = float(latest_row["MACD_Hist"])

    if trend_state == 1:
        if macd_hist > 0 and rsi < 70:
            trend_label = "強力な上昇トレンド (STRONG BULL)"
            recommendation = "即時ロング (Immediate Buy)" if prob_percent >= 65 else "待機 (Wait for Pullback)"
        else:
            trend_label = "上昇トレンド (BULL)"
            recommendation = "押し目買い検討 (Consider Buy)"
    elif trend_state == -1:
        if macd_hist < 0 and rsi > 30:
            trend_label = "強力な下降トレンド (STRONG BEAR)"
            recommendation = "即時ショート (Immediate Sell)" if prob_percent >= 65 else "待機 (Wait for Bounce)"
        else:
            trend_label = "下降トレンド (BEAR)"
            recommendation = "戻り売り検討 (Consider Sell)"
    else:
        trend_label = "レンジ / トレンド転換期 (NEUTRAL)"
        recommendation = "様子見 (Watch & Wait)"

    return {
        "current_price": close_price,
        "success_probability": prob_percent,
        "trend_label": trend_label,
        "entry_recommendation": recommendation,
        "atr_pips": atr_pips,
        "rsi": rsi,
        "target_pips": target_pips,
        "target_price_delta": target_pips * pip_scale,
        "feature_importance": importances
    }


def analyze_all_gmo_pairs(target_pips: float = 250, history_df: pd.DataFrame = None) -> pd.DataFrame:
    """全10通貨ペア分析"""
    results = []
    pairs_data_map = {}

    for pair_name, config in GMO_PAIRS.items():
        ticker = config["ticker"]
        pip_scale = config["pip_scale"]

        df = fetch_forex_data(ticker, period="1y", interval="1d")
        if df.empty or len(df) < 50:
            continue

        df_feat = generate_technical_features(df, pip_scale=pip_scale)
        pairs_data_map[pair_name] = df_feat

        analysis = train_and_predict_probability(
            df_feat,
            pip_scale=pip_scale,
            target_pips=target_pips,
            pair_name=pair_name,
            history_df=history_df
        )

        unit = "円" if config["type"] == "JPY" else "ドル"
        target_val = round(analysis["target_price_delta"], 4)

        results.append({
            "通貨ペア": pair_name,
            "現在値": analysis["current_price"],
            "AI成功確率 (%)": analysis["success_probability"],
            "推奨タイミング": analysis["entry_recommendation"],
            "大局トレンド": analysis["trend_label"],
            "目標利益幅": f"{target_pips} pips ({target_val}{unit})",
            "日足ATR (pips)": analysis["atr_pips"],
            "RSI (14)": analysis["rsi"],
            "ティッカー": ticker
        })

    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df.sort_values(by="AI成功確率 (%)", ascending=False, inplace=True)
        result_df.reset_index(drop=True, inplace=True)

    return result_df


if __name__ == "__main__":
    print("=== GMO FX AI Quant Model Test Execution ===")
    df_results = analyze_all_gmo_pairs(target_pips=250)
    print(df_results.to_string())


# ==========================================
# FILE: notifier.py
# ==========================================

"""
GMO FX AI Quant Analysis - Email Notification Module
(SMTPメール自動送信・シグナル通知モジュール)
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def send_smtp_email(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    receiver_email: str = "huashenfo@gmail.com",
    subject: str = "",
    body_html: str = ""
) -> bool:
    """
    SMTPサーバーを利用してHTMLメールを送信します。

    :param smtp_server: SMTPサーバーアドレス (例: smtp.gmail.com)
    :param smtp_port: ポート番号 (587: TLS / 465: SSL)
    :param sender_email: 送信元メールアドレス
    :param sender_password: Appパスワードまたはアクセスコード
    :param receiver_email: 送信先メールアドレス
    :param subject: 件名
    :param body_html: 本文 (HTML形式)
    :return: 送信成功時 True, 失敗時 False
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        html_part = MIMEText(body_html, "html", "utf-8")
        msg.attach(html_part)

        logging.info(f"Connecting to SMTP Server: {smtp_server}:{smtp_port}")

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
    """
    AI計算結果データからメール通知用の美しく洗練されたHTMLボディを生成します。

    :param signals_df: 通貨ペアの分析結果DataFrame
    :param threshold_pct: メール送信対象とするAI確率しきい値 (%)
    :return: HTML文字列
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # しきい値以上の高確率シグナルを抽出
    top_signals = signals_df[signals_df["AI成功確率 (%)"] >= threshold_pct]

    rows_html = ""
    for idx, row in signals_df.iterrows():
        is_highlight = row["AI成功確率 (%)"] >= threshold_pct
        bg_style = "background-color: #f0fdf4;" if is_highlight else ""
        badge_style = "background-color: #16a34a; color: white;" if is_highlight else "background-color: #6b7280; color: white;"

        rows_html += f"""
        <tr style="{bg_style} border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; font-weight: bold; color: #111827;">{row['通貨ペア']}</td>
            <td style="padding: 12px; font-size: 16px; font-weight: bold; color: #2563eb;">{row['現在値']}</td>
            <td style="padding: 12px;">
                <span style="padding: 4px 8px; border-radius: 4px; font-weight: bold; {badge_style}">
                    {row['AI成功確率 (%)']}%
                </span>
            </td>
            <td style="padding: 12px; color: #059669; font-weight: bold;">{row['推奨タイミング']}</td>
            <td style="padding: 12px; color: #4b5563;">{row['大局トレンド']}</td>
            <td style="padding: 12px; color: #4b5563;">{row['目標利益幅']}</td>
            <td style="padding: 12px; color: #4b5563;">{row['日足ATR (pips)']} pips</td>
        </tr>
        """

    highlight_summary = ""
    if not top_signals.empty:
        highlight_summary = f"""
        <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 16px; margin-bottom: 20px; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; color: #065f46;">🚨 高確率シグナル点灯 ({len(top_signals)}件)</h3>
            <p style="margin: 0; color: #047857; font-size: 14px;">
                確率 {threshold_pct}% 以上のエントリー推奨通貨ペアが検出されました。最優先検討ペア: <strong>{top_signals.iloc[0]['通貨ペア']} ({top_signals.iloc[0]['AI成功確率 (%)']}%)</strong>
            </p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>GMO FX AI Quant Signal Alert</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px; margin: 0;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px;">
                <h1 style="color: #1e3a8a; margin: 0; font-size: 22px;">🤖 GMO FX AI Quant - 大局トレンド & 200〜300pips到達確率通知</h1>
                <p style="color: #6b7280; font-size: 12px; margin: 4px 0 0 0;">データ更新日時: {now_str}</p>
            </div>

            {highlight_summary}

            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                <thead>
                    <tr style="background-color: #1e293b; color: #ffffff;">
                        <th style="padding: 10px;">通貨ペア</th>
                        <th style="padding: 10px;">現在値</th>
                        <th style="padding: 10px;">AI成功確率</th>
                        <th style="padding: 10px;">推奨タイミング</th>
                        <th style="padding: 10px;">大局トレンド</th>
                        <th style="padding: 10px;">目標利益幅</th>
                        <th style="padding: 10px;">ATR</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #9ca3af; text-align: center;">
                ※ 本メールはGMO FX AI Quantシステムによる自動判定通知です。投資に関する最終決定はご自身の判断で行ってください。
            </div>
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    print("=== Notifier Module Ready ===")
