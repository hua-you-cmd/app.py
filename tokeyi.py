# ==========================================
# FILE: app.py
# ==========================================

"""
GMO / SBI FX AI Quant Analysis - Streamlit Web Application
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

# 自作モジュールのインポート（notifier のインポートは削除済み）
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
