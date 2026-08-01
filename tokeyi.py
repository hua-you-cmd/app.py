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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def build_signal_email_html(pair_name: str, action: str, price: float, prob: float, rsi: float) -> str:
    """シグナル検知時の通知メールHTMLを作成"""
    color = "#10B981" if action == "BUY" else "#EF4444"
    action_label = "【買いシグナル】" if action == "BUY" else "【売りシグナル】"
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px;">
          <h2 style="color: {color}; margin-top: 0;">{action_label} {pair_name}</h2>
          <p style="font-size: 16px; color: #333333;">条件を満たすシグナルが検知されました。</p>
          <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">通貨ペア</td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pair_name}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">現在価格</td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{price}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">予測確率</td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prob}%</td>
            </tr>
            <tr>
              <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">RSI</td>
              <td style="padding: 8px; border-bottom: 1px solid #ddd;">{rsi}</td>
            </tr>
          </table>
        </div>
      </body>
    </html>
    """
    return html


def send_smtp_email(smtp_server: str, port: int, sender_email: str, password: str, receiver_email: str, subject: str, html_content: str) -> bool:
    """SMTPを使用してメールを送信"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


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
                    st.error("❌ パスコードが正しくありません")
    st.stop()


# 3. セッション状態の初期化
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None


# 4. ヘルパー関数: 分析実行
def run_analysis(target_pips: int):
    with st.spinner("Yahoo Financeから最新データを取得し、AIモデルで確率を計算中..."):
        df_results = analyze_all_gmo_pairs(target_pips=target_pips)
        st.session_state.analysis_results = df_results
        st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 5. ヘルパー関数: Gemini AI マクロ分析 (純粋なPython処理)
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
    st.caption("GMO為替10銘柄に対応。マクロトレンドとボラティリティを学習し、期待値の最も高い時期をAI判定します。")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 最新データ再計算", type="primary"):
        run_analysis(target_pips_setting)


# 初期データ実行
if st.session_state.analysis_results is None:
    run_analysis(target_pips_setting)

df_res = st.session_state.analysis_results
last_time = st.session_state.last_updated

st.info(f"🕒 最終データ更新日時: **{last_time}** (Yahoo Finance リアルタイムデータ連動)")


# 8. ハイライト KPI カード
if df_res is not None and len(df_res) > 0:

    
if df_res is not None and len(df_res) > 0:
    df_res_df = pd.DataFrame(df_res) if isinstance(df_res, list) else df_res
    top_pair = df_res_df.iloc[0]  # これなら .iloc[0] が使える


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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 確率ランキング MATRIX",
        "📈 詳細テクニカルチャート",
        "✨ Gemini AI マクロ解説",
        "📋 全ソースコード一括表示/コピー"
    ])

    # TAB 1: Ranking Table
    with tab1:
        st.subheader("GMO為替 10銘柄 確率ランキング")

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

    # TAB 2: Detailed Technical Charts
    with tab2:
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

    # TAB 3: Gemini AI Macro Insight
    with tab3:
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

    # TAB 4: Python Full Code Exporter (Pythonコード専用コピー & ダウンロード)
    with tab4:
        st.subheader("🐍 Python専用 ソースコード一括表示 & ダウンロード")
        st.caption("コードの途切れを防止するため、1クリックでのファイル直接ダウンロード (.py) とコピー用テキストボックスを完備しています。")

        # 1. tokeyi.py 単一完全独立ファイル
        if os.path.exists("tokeyi.py"):
            with open("tokeyi.py", "r", encoding="utf-8") as f:
                tokeyi_code = f.read()
            st.markdown("### ⚡ 1. tokeyi.py (単一完全独立 Python スクリプト)")
            st.success("💡 1つのPythonファイルのみで動作させたい場合は、以下のダウンロードボタンまたはテキストボックスをご利用ください。")
            
            st.download_button(
                label="📥 tokeyi.py を直接ダウンロード",
                data=tokeyi_code,
                file_name="tokeyi.py",
                mime="text/x-python",
                type="primary"
            )
            st.text_area("tokeyi.py 全ソースコード (全選択 Ctrl+A -> Ctrl+C で確実に完全コピー可能):", value=tokeyi_code, height=400)

        st.markdown("---")

        # Pythonコード専用束 (tokeyi.py + app.py + model.py + notifier.py)
        python_files = [
            ("tokeyi.py (単一独立スクリプト)", "tokeyi.py"),
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

        st.markdown("### 🐍 2. Python全ファイル一括結合コード (tokeyi.py + app.py + model.py + notifier.py)")
        st.download_button(
            label="📥 Python全コード一括ファイルをダウンロード (all_python_code.py)",
            data=python_code_text,
            file_name="all_python_code.py",
            mime="text/x-python"
        )
        st.text_area("Python全コード一括テキスト (Ctrl+A -> Ctrl+C で確実に完全コピー可能):", value=python_code_text, height=500)

        st.markdown("---")
        st.markdown("### 📄 3. Python個別ファイル別ダウンロード & 表示")
        for label, filepath in python_files:
            if os.path.exists(filepath):
                with st.expander(f"📄 {filepath} — {label}"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_code = f.read()
                    st.download_button(
                        label=f"📥 {filepath} をダウンロード",
                        data=file_code,
                        file_name=filepath,
                        mime="text/x-python",
                        key=f"dl_{filepath}"
                    )
                    st.text_area(f"{filepath} コード:", value=file_code, height=350, key=f"ta_{filepath}")

st.markdown("---")
st.caption("© 2026 GMO FX AI Quant System | Passcode: 5689 | Powered by Python & Streamlit")


# ==========================================
# FILE: model.py
# ==========================================

"""
GMO FX AI Quant Analysis - ML Model & Feature Engineering Module
(データ取得、特徴量生成、機械学習モデル学習、200〜300pips到達確率算出バックエンド)
"""

import json
import logging
import math
import urllib.request
import urllib.parse
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

# 既存のtokeyi.py / app.pyとの完全な互換性を保つためのエイリアス
TARGET_PAIRS = SBI_PAIRS
GMO_PAIRS = {pair["name"]: pair for pair in SBI_PAIRS}


def fetch_forex_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Yahoo Financeから指定した通貨ペアのリアルタイム・ヒストリカル価格データを取得します。
    標準ライブラリ(urllib)によるYahoo Finance REST API直接取得と、yfinanceライブラリのハイブリッド型。

    :param symbol: Yahoo Financeティッカー (例: 'USDJPY=X')
    :param period: 取得期間 ('1mo', '1y', '2y')
    :param interval: 時間軸 ('1d', '1h')
    :return: OHLCVデータのPandas DataFrame
    """
    ticker_symbol = symbol

    # 方法1: Yahoo Finance Query v8 API 直接取得 (最も確実)
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
                logging.info(f"Successfully fetched {len(df)} candles for {ticker_symbol} via Yahoo REST API.")
                return df
    except Exception as e:
        logging.warning(f"Direct Yahoo REST API fetch failed for {ticker_symbol}: {e}")

    # 方法2: yfinance ライブラリ
    if YFINANCE_AVAILABLE:
        try:
            logging.info(f"Downloading data for ticker via yfinance: {ticker_symbol}")
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
    """
    マクロトレンドおよびモメンタム、ボラティリティの技術指標（特徴量）を生成します。
    """
    if df.empty:
        return df

    data = df.copy()

    # 1. 移動平均線 (SMA)
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["SMA_200"] = data["Close"].rolling(window=200).mean()

    # 2. 指数平滑移動平均線 (EMA)
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()

    # 3. MACD (12, 26, 9)
    data["MACD"] = data["EMA_12"] - data["EMA_26"]
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]

    # 4. ATR (Average True Range: 14日) - リスク・ボラティリティ指標
    high_low = data["High"] - data["Low"]
    high_close = (data["High"] - data["Close"].shift(1)).abs()
    low_close = (data["Low"] - data["Close"].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    data["ATR"] = true_range.rolling(window=14).mean()
    data["ATR_Pips"] = data["ATR"] / pip_scale

    # 5. RSI (14日)
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    data["RSI"] = 100 - (100 / (1 + rs))

    # 6. ボリンジャーバンド (20日, 2σ)
    std_20 = data["Close"].rolling(window=20).std()
    data["BB_Upper"] = data["SMA_20"] + (std_20 * 2)
    data["BB_Lower"] = data["SMA_20"] - (std_20 * 2)
    data["BB_Width"] = (data["BB_Upper"] - data["BB_Lower"]) / data["SMA_20"]

    # 7. トレンド乖離率・マクロ特徴量
    data["Dist_SMA200"] = (data["Close"] - data["SMA_200"]) / data["SMA_200"]
    data["Dist_SMA50"] = (data["Close"] - data["SMA_50"]) / data["SMA_50"]
    data["Return_5D"] = data["Close"].pct_change(5)
    data["Return_20D"] = data["Close"].pct_change(20)

    # トレンド方向判定 (1: 上昇トレンド, -1: 下降トレンド, 0: レンジ)
    data["Trend_State"] = 0
    data.loc[(data["Close"] > data["SMA_50"]) & (data["SMA_50"] > data["SMA_200"]), "Trend_State"] = 1
    data.loc[(data["Close"] < data["SMA_50"]) & (data["SMA_50"] < data["SMA_200"]), "Trend_State"] = -1

    return data.dropna()


def create_target_label(df: pd.DataFrame, pip_scale: float, target_pips: float = 250, forward_days: int = 10) -> pd.Series:
    """
    【AI学習用の正解ラベル生成】
    今後 forward_days (例: 10営業日) 以内に、200〜300pips (デフォルト250pips = 2.5円) の利益幅を
    利確ターゲットとして到達したかどうか（1: 成功 / 0: 不成功）を判定します。

    :param df: OHLCデータ
    :param pip_scale: pip倍率
    :param target_pips: 目標pips (200~300pips)
    :param forward_days: 先行評価期間
    :return: 0 or 1 のバイナリラベル
    """
    target_distance = target_pips * pip_scale

    # 未来の最高値・最安値をローリング取得
    future_high_max = df["High"].iloc[::-1].rolling(window=forward_days).max().iloc[::-1]
    future_low_min = df["Low"].iloc[::-1].rolling(window=forward_days).min().iloc[::-1]

    # 上昇トレンドで +target_distance 以上上昇、または下降トレンドで -target_distance 以上下落
    long_profit = (future_high_max - df["Close"]) >= target_distance
    short_profit = (df["Close"] - future_low_min) >= target_distance

    # 正解ラベル: トレンド方向への利確幅達成
    target = np.where(
        (df["Trend_State"] == 1) & long_profit, 1,
        np.where((df["Trend_State"] == -1) & short_profit, 1, 0)
    )

    return pd.Series(target, index=df.index)


def train_and_predict_probability(df: pd.DataFrame, pip_scale: float, target_pips: float = 250) -> dict:
    """
    Random Forest機械学習モデルを学習させ、現在足における「200〜300pips獲得成功確率」を計算します。

    :return: 確率(%), トレンド方向, 特徴量貢献度などの辞書オブジェクト
    """
    feature_cols = [
        "MACD", "MACD_Hist", "RSI", "ATR_Pips", "BB_Width",
        "Dist_SMA200", "Dist_SMA50", "Return_5D", "Return_20D", "Trend_State"
    ]

    target = create_target_label(df, pip_scale, target_pips=target_pips)
    data = df.copy()
    data["Target"] = target

    # 直近の正解ラベルが未確定（未来データなし）の行を除外して学習データセット構築
    clean_data = data.dropna(subset=feature_cols + ["Target"])
    train_df = clean_data.iloc[:-10] # 最新10日は未来ラベル未判定のため除外

    if len(train_df) < 50:
        return {
            "success_probability": 50.0,
            "trend_label": "判定不能",
            "entry_recommendation": "データ不足",
            "feature_importance": {}
        }

    X_train = train_df[feature_cols]
    y_train = train_df["Target"]

    # ランダムフォレストモデル定義
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # 最新足（現時点）の特徴量で予測確率を算出
    latest_features = df[feature_cols].iloc[[-1]]
    prob_class1 = model.predict_proba(latest_features)[0][1] # クラス1 (到達成功) の確率
    prob_percent = round(float(prob_class1 * 100), 1)

    # 特徴量貢献度の取得
    importances = dict(zip(feature_cols, [round(float(v), 3) for v in model.feature_importances_]))

    # 最新足のデータ取得
    latest_row = df.iloc[-1]
    close_price = float(latest_row["Close"])
    atr_pips = round(float(latest_row["ATR_Pips"]), 1)
    trend_state = int(latest_row["Trend_State"])
    rsi = round(float(latest_row["RSI"]), 1)
    macd_hist = float(latest_row["MACD_Hist"])

    # トレンド方向とエントリー判定ロジック
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


def analyze_all_gmo_pairs(target_pips: float = 250) -> pd.DataFrame:
    """
    GMO 10通貨ペアすべてのデータを一括取得・解析し、狙い目順にソートした結果を返します。
    """
    results = []

    for pair_name, config in GMO_PAIRS.items():
        ticker = config["ticker"]
        pip_scale = config["pip_scale"]

        df = fetch_forex_data(ticker, period="1y", interval="1d")
        if df.empty or len(df) < 50:
            continue

        df_feat = generate_technical_features(df, pip_scale=pip_scale)
        analysis = train_and_predict_probability(df_feat, pip_scale=pip_scale, target_pips=target_pips)

        # ドルペアと円ペアでターゲット単位の整形
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
