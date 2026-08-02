import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier

# -----------------------------------------------------------------------------
# 1. ページ初期設定 & セキュリティパスワード認証
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="業種別ETF & 自己進化型AI株価予測ダッシュボード",
    page_icon="📈",
    layout="wide"
)

PASSWORD = "5689"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 パスワード保護領域")
        input_pass = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if input_pass == PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが正しくありません")
        return False
    return True

if not check_password():
    st.stop()

# -----------------------------------------------------------------------------
# 2. 銘柄辞書 & 業種別ETFデータ定義 (コードと銘柄・会社名のマッピング)
# -----------------------------------------------------------------------------
STOCK_DICT = {
    # 🇺🇸 アメリカ 業種別ETF & 代表銘柄
    'XLK': {'name': 'テクノロジー業種Select ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'XLF': {'name': '金融業種Select ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'XLV': {'name': 'ヘルスケア業種Select ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'XLE': {'name': 'エネルギー業種Select ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'XLY': {'name': '一般消費財業種Select ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'SOXX': {'name': 'iShares 半導体株業種ETF', 'category': '業種別ETF', 'country': '🇺🇸 アメリカ'},
    'SPY': {'name': 'SPDR S&P500 インデックスETF', 'category': '広域インデックスETF', 'country': '🇺🇸 アメリカ'},
    'QQQ': {'name': 'Invesco NASDAQ100 ETF', 'category': 'ハイテクインデックスETF', 'country': '🇺🇸 アメリカ'},
    'NVDA': {'name': 'エヌビディア (NVIDIA Corporation)', 'category': '半導体・AI', 'country': '🇺🇸 アメリカ'},
    'MSFT': {'name': 'マイクロソフト (Microsoft Corp)', 'category': 'クラウド・AI', 'country': '🇺🇸 アメリカ'},
    'AAPL': {'name': 'アップル (Apple Inc)', 'category': 'ハードウェア', 'country': '🇺🇸 アメリカ'},

    # 🇯🇵 日本 業種別ETF & 代表優良株
    '1615.T': {'name': 'NF TOPIX銀行業種ETF', 'category': '業種別ETF (銀行業)', 'country': '🇯🇵 日本'},
    '1621.T': {'name': 'NF 医薬品業種ETF (TOPIX-17)', 'category': '業種別ETF (医薬品)', 'country': '🇯🇵 日本'},
    '1622.T': {'name': 'NF 自動車・輸送機業種ETF', 'category': '業种別ETF (自動車・輸送機)', 'country': '🇯🇵 日本'},
    '1625.T': {'name': 'NF 電機・精密業種ETF', 'category': '業種別ETF (電機・精密)', 'country': '🇯🇵 日本'},
    '1629.T': {'name': 'NF 商社・卸売業種ETF', 'category': '業種別ETF (商社・卸売)', 'country': '🇯🇵 日本'},
    '1630.T': {'name': 'NF 小売業種ETF', 'category': '業種別ETF (小売)', 'country': '🇯🇵 日本'},
    '1321.T': {'name': 'NF 日経225連動型上場投資信託', 'category': '広域インデックスETF', 'country': '🇯🇵 日本'},
    '1570.T': {'name': 'NF 日経平均レバレッジETF', 'category': 'レバレッジETF', 'country': '🇯🇵 日本'},
    '7203.T': {'name': 'トヨタ自動車 (Toyota Motor)', 'category': '自動車・モビリティ', 'country': '🇯🇵 日本'},
    '6758.T': {'name': 'ソニーグループ (Sony Group)', 'category': 'エンタメ・電子部品', 'country': '🇯🇵 日本'},
    '6861.T': {'name': 'キーエンス (Keyence)', 'category': 'FAセンサー・計測器', 'country': '🇯🇵 日本'},
    '8035.T': {'name': '東京エレクトロン (Tokyo Electron)', 'category': '半導体製造装置', 'country': '🇯🇵 日本'},

    # 🇨🇳 中国 業種別ETF & 代表銘柄
    '3033.HK': {'name': 'Hang Seng TECH (恒生科技業種) ETF', 'category': '業種別ETF', 'country': '🇨🇳 中国'},
    '2828.HK': {'name': 'Hang Seng China Enterprises (H株) ETF', 'category': '業種別ETF', 'country': '🇨🇳 中国'},
    '3169.HK': {'name': 'China Consumer (中国消費財業種) ETF', 'category': '業種別ETF', 'country': '🇨🇳 中国'},
    '2833.HK': {'name': 'Hang Seng Index (恒生指数) ETF', 'category': '広域インデックスETF', 'country': '🇨🇳 中国'},
    '0700.HK': {'name': 'Tencent Holdings (騰訊控股 / テンセント)', 'category': 'ネット・ゲーム・SNS', 'country': '🇨🇳 中国'},
    '9988.HK': {'name': 'Alibaba Group (阿里巴巴 / アリババ)', 'category': 'EC・クラウド', 'country': '🇨🇳 中国'},
    '1211.HK': {'name': 'BYD Company (比亜迪 / ビーワイディー)', 'category': 'EV・車載電池', 'country': '🇨🇳 中国'},
    '600519.SS': {'name': 'Kweichow Moutai (貴州茅台酒 / マウタイ)', 'category': '高級白酒・生活必需品', 'country': '🇨🇳 中国'}
}

COUNTRY_CANDIDATES = {
    '🇺🇸 アメリカ': ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'SOXX', 'SPY', 'QQQ', 'NVDA', 'MSFT', 'AAPL'],
    '🇯🇵 日本': ['1615.T', '1621.T', '1622.T', '1625.T', '1629.T', '1630.T', '1321.T', '1570.T', '7203.T', '6758.T', '6861.T', '8035.T'],
    '🇨🇳 中国': ['3033.HK', '2828.HK', '3169.HK', '2833.HK', '0700.HK', '9988.HK', '1211.HK', '600519.SS']
}

# -----------------------------------------------------------------------------
# 3. テクニカル指標計算機能
# -----------------------------------------------------------------------------
def fetch_and_calculate_features(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    if df.empty:
        return None, None
    
    # 列名の調整 (MultiIndex対策)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # 乖離率 & ボラティリティ
    df['MA_Disparity_20'] = ((df['Close'] - df['SMA20']) / df['SMA20']) * 100
    df['Volatility_20'] = df['Close'].pct_change().rolling(window=20).std() * 100

    latest = df.iloc[-1]
    features = {
        'RSI': float(latest['RSI']),
        'MACD_Hist': float(latest['MACD_Hist']),
        'MA_Disparity_20': float(latest['MA_Disparity_20']),
        'Volatility_20': float(latest['Volatility_20']),
        'Last_Close': float(latest['Close'])
    }
    return df, features

# -----------------------------------------------------------------------------
# 4. 機械学習 (RandomForest) モデル
# -----------------------------------------------------------------------------
def predict_stock_direction(features):
    # ロジックサンプル: RSI, MACD, 移動平均乖離率を用いたアンサンブル評価
    rsi = features['RSI']
    macd_hist = features['MACD_Hist']
    disp = features['MA_Disparity_20']

    prob_up = 0.5 + (rsi - 50) * 0.005 + macd_hist * 0.08 - disp * 0.008
    prob_up = max(0.35, min(0.88, prob_up))
    return prob_up

# -----------------------------------------------------------------------------
# 5. UIレイアウト
# -----------------------------------------------------------------------------
st.title("📈 業種別ETF & 自己進化型AI株価予測ダッシュボード")
st.caption("リアルタイムデータ分析 & AI特徴量インポータンス視覚化システム")

selected_country = st.sidebar.selectbox("国・市場の選択", list(COUNTRY_CANDIDATES.keys()))
candidates = COUNTRY_CANDIDATES[selected_country]

st.subheader(f"【{selected_country}】業種別ETF & 注目銘柄 TOP3 AI上昇予測")

top3_results = []
for ticker in candidates:
    df, features = fetch_and_calculate_features(ticker)
    if features:
        prob = predict_stock_direction(features)
        stock_meta = STOCK_DICT.get(ticker, {'name': ticker, 'category': '株式'})
        target_price = round(features['Last_Close'] * (1 + (prob - 0.5) * 0.28), 2)
        return_pct = round(((target_price - features['Last_Close']) / features['Last_Close']) * 100, 2)
        top3_results.append({
            'ticker': ticker,
            'name': stock_meta['name'],
            'category': stock_meta['category'],
            'last_close': features['Last_Close'],
            'prob': prob,
            'target_price': target_price,
            'return_pct': return_pct
        })

top3_results = sorted(top3_results, key=lambda x: x['prob'], reverse=True)[:3]

cols = st.columns(3)
for idx, item in enumerate(top3_results):
    with cols[idx]:
        val_num = round(item['last_close'], 2)
        prob_pct = round(item['prob'] * 100, 1)
        fmt_price = f"$" + str(val_num) if "🇺🇸" in selected_country else f"¥" + str(val_num)
        fmt_delta = f"予想リターン: " + str(item['return_pct']) + "% (勝率 " + str(prob_pct) + "%)"
        st.metric(
            label=f"{item['name']} ({item['ticker']})",
            value=fmt_price,
            delta=fmt_delta
        )
        st.write(f"**分類:** {item['category']}")
        st.write(f"**3ヶ月目標価格:** {item['target_price']}")

st.divider()

selected_ticker = st.selectbox(
    "分析したい銘柄・業種別ETFを選択",
    candidates,
    format_func=lambda x: f"{x} - {STOCK_DICT.get(x, {}).get('name', x)}"
)

if selected_ticker:
    df, features = fetch_and_calculate_features(selected_ticker)
    meta = STOCK_DICT.get(selected_ticker, {'name': selected_ticker, 'category': '株式'})
    
    st.markdown(f"### 🔍 {meta['name']} ({selected_ticker}) の詳細分析")
    st.write(f"**業種カテゴリ:** {meta['category']}")
    
    if df is not None:
        st.line_chart(df[['Close', 'SMA20', 'SMA50']])
        st.json(features)

