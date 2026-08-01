# ==========================================
# FILE: tokeyi.py
# ==========================================

"""
GMO / SBI FX クオンツAI予測ダッシュボード (tokeyi.py - 完全独立スタンドアロン版)
Yahoo Financeから主要10通貨ペアデータをリアルタイム取得し、
機械学習(RandomForest)とテクニカル指標(SMA, RSI, MACD, ATR, Bollinger)から目標pips到達確率を算出・可視化します。
外部の自作モジュールに一切依存せず単体で動作します。
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


# --- 2. メール送信機能 (完全インライン独立関数) ---
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


# --- 3. クオンツ分析データ取得 & 計算エンジン ---
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


def train_and_predict_probability(df: pd.DataFrame, target_pips: float = 250.0, pip_scale: float = 0.01) -> dict:
    """RandomForestを用いて、買い(Long)および売り(Short)での目標pips到達確率を予測"""
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

    X = valid_df[feature_cols]
    y_long = valid_df["Long_Target_Reached"]

    rf_long = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_long.fit(X, y_long)

    latest_features = X.iloc[[-1]]

    # 買い確率の安全取得（IndexError防止）
    long_probs = rf_long.predict_proba(latest_features)[0]
    long_prob_raw = long_probs[1] if len(long_probs) > 1 else (1.0 if y_long.iloc[-1] == 1 else 0.0)

    # 売り確率の安全取得（IndexError防止）
    y_short = valid_df["Short_Target_Reached"]
    rf_short = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_short.fit(X, y_short)

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


def analyze_all_gmo_pairs(period: str = "1y", target_pips: float = 250.0) -> list:
    """全10通貨ペアのデータを一括で取得・分析"""
    results = []
    for pair in SBI_PAIRS:
        df = fetch_forex_data(pair["symbol"], period=period)
        if not df.empty:
            df = generate_technical_features(df, pip_scale=pair["pip_scale"])
            pred = train_and_predict_probability(df, target_pips=target_pips, pip_scale=pair["pip_scale"])
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


# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="GMO / SBI FX AI Quant Predictor", layout="wide", page_icon="📈")

st.title("📈 SBI / GMO FX AI クオンツ到達確率予測システム")
st.caption("Yahoo Finance 100%リアルタイムデータ ＆ RandomForest機械学習モデル (単一完全独立スクリプト)")

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

with st.spinner("Yahoo Financeからリアルタイムデータを取得中..."):
    results = analyze_all_gmo_pairs(target_pips=target_pips_setting)

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
    st.subheader(f"📊 主要10通貨ペア {target_pips_setting}pips 到達確率一覧")
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

st.caption("© 2026 GMO FX AI Quant System")


# ==========================================
# FILE: app.py
# ==========================================

"""
GMO FX AI Quant Analysis - Streamlit Web Application
(100% 独立・完全動作 Python/Streamlit ダッシュボード)
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 自作モジュールのインポート
from model import GMO_PAIRS, analyze_all_gmo_pairs, fetch_forex_data, generate_technical_features
from notifier import build_signal_email_html, send_smtp_email

# 1. ページ基本設定
st.set_page_config(
    page_title="GMO FX AI Quant - 200〜300pips到達確率判定システム",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS (ネオ・ブルータリズム風グラファイトデザイン)
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
                    st.error("
