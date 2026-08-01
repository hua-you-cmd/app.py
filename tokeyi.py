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
    st.caption("本システムは保護されています。パスワード【5689】を入力してログインしてください。")

    col_lock1, col_lock2 = st.columns([2, 1])
    with col_lock1:
        passcode_input = st.text_input("パスワードを入力:", type="password", placeholder="5689")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("パスワード5689を自動入力"):
                passcode_input = "5689"
                st.session_state.authenticated = True
                st.rerun()
        with col_btn2:
            if st.button("ログイン (Unlock)", type="primary"):
                if passcode_input == "5689":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ パスワードが正しくありません (ヒント: 5689)")
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
receiver_email = st.sidebar.text_input("送信先 Email", value="")

if st.sidebar.button("🔒 再ロック (ログアウト)"):
    st.session_state.authenticated = False
    st.rerun()


# 7. メインヘッダー
col_title, col_btn = st.columns([3, 1])

with col_title:
    st.title("🤖 GMO FX AI Quant - 200〜300pips到達確率モニター")
    st.caption("GMO為替10銘柄に対応。マクロトレンドとボラティリティを学習し、期待値の最も高い時期をAI判定します。(Passcode: 5689)")

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

    # TAB 4: Full Code Exporter (Streamlitで全コードコピー)
    with tab4:
        st.subheader("🐍 Python専用 ＆ 全ソースコード一括コピー")
        st.caption("コードブロックの右上にある『📋 コピー』アイコンをクリックしてコピーできます。")

        # Pythonコード専用束 (app.py + model.py + notifier.py)
        python_files = [
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

        st.markdown("### 🐍 1. Pythonコード専用 一括コピー (app.py + model.py + notifier.py)")
        st.info("💡 以下のコード枠の右上ホバーで出現する『📋 コピー』ボタンを押すと、Python全コードをクリップボードに一括コピーできます。")
        st.code(python_code_text, language="python")

        st.markdown("---")

        # 全コード束
        all_files = python_files + [
            ("server.ts (Node Express API サーバー)", "server.ts"),
            ("package.json (依存ライブラリ一覧)", "package.json")
        ]

        full_code_text = ""
        for label, filepath in all_files:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    full_code_text += f"# ==========================================\n# FILE: {filepath}\n# ({label})\n# ==========================================\n\n{content}\n\n"

        st.markdown("### 📁 2. プロジェクト全ファイル一括コピー (Python + Server + Config)")
        st.code(full_code_text, language="python")

        st.markdown("---")
        st.markdown("### 📄 3. 個別ファイル別ソースコード")
        for label, filepath in all_files:
            if os.path.exists(filepath):
                with st.expander(f"📄 {filepath} — {label}"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_code = f.read()
                    lang = "python" if filepath.endswith(".py") else "json" if filepath.endswith(".json") else "typescript"
                    st.code(file_code, language=lang)

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

# 1. GMO為替メインレート 10通貨ペアの定義と設定
# 各通貨ペアのYahoo Financeティッカー、通貨属性、1pipの定義(円ペア:0.01 / ドルペア:0.0001)
GMO_PAIRS = {
    "USD/JPY": {"ticker": "USDJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},  # 2.5円幅 (250pips)
    "EUR/JPY": {"ticker": "EURJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "GBP/JPY": {"ticker": "GBPJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "AUD/JPY": {"ticker": "AUDJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "NZD/JPY": {"ticker": "NZDJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "CAD/JPY": {"ticker": "CADJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "CHF/JPY": {"ticker": "CHFJPY=X", "type": "JPY", "pip_scale": 0.01, "target_pips": 250},
    "EUR/USD": {"ticker": "EURUSD=X", "type": "USD", "pip_scale": 0.0001, "target_pips": 250}, # 0.0250ドル幅 (250pips)
    "GBP/USD": {"ticker": "GBPUSD=X", "type": "USD", "pip_scale": 0.0001, "target_pips": 250},
    "AUD/USD": {"ticker": "AUDUSD=X", "type": "USD", "pip_scale": 0.0001, "target_pips": 250},
}


def fetch_forex_data(ticker_symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Yahoo Financeから指定した通貨ペアのリアルタイム・ヒストリカル価格データを100%取得します。
    標準ライブラリ(urllib)によるYahoo Finance REST API直接取得と、yfinanceライブラリのハイブリッド型。

    :param ticker_symbol: Yahoo Financeティッカー (例: 'USDJPY=X')
    :param period: 取得期間 ('1y', '2y')
    :param interval: 時間軸 ('1d', '1h')
    :return: OHLCVデータのPandas DataFrame
    """
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
            df = yf.download(ticker_symbol, period=period, interval=interval, progress=False)

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

    :param df: OHLC価格データ
    :param pip_scale: pips計算用のスケール (JPYペア: 0.01, USDペア: 0.0001)
    :return: 特徴量が追加されたDataFrame
    """
    data = df.copy()

    # 1. 移動平均線 (SMA)
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
    receiver_email: str,
    subject: str,
    body_html: str
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
