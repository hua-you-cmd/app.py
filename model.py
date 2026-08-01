# ==========================================
# FILE: model.py
# ==========================================

import yfinance as yf
import pandas as pd

# SBI / GMO 為替メイン10通貨ペアの定義
SBI_PAIRS = [
    {"symbol": "AUDUSD=X", "name": "AUD/USD", "disp": "豪ドル/米ドル", "pip_scale": 0.0001},
    {"symbol": "USDJPY=X", "name": "USD/JPY", "disp": "米ドル/円", "pip_scale": 0.01},
    {"symbol": "EURJPY=X", "name": "EUR/JPY", "disp": "ユーロ/円", "pip_scale": 0.01},
    {"symbol": "GBPJPY=X", "name": "GBP/JPY", "disp": "ポンド/円", "pip_scale": 0.01},
    {"symbol": "AUDJPY=X", "name": "AUD/JPY", "disp": "豪ドル/円", "pip_scale": 0.01},
    {"symbol": "NZDJPY=X", "name": "NZD/JPY", "disp": "NZドル/円", "pip_scale": 0.01},
    {"symbol": "CADJPY=X", "name": "CAD/JPY", "disp": "カナダドル/円", "pip_scale": 0.01},
    {"symbol": "CHFJPY=X", "name": "CHF/JPY", "disp": "スイスフラン/円", "pip_scale": 0.01},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "disp": "ポンド/米ドル", "pip_scale": 0.0001},
    {"symbol": "EURUSD=X", "name": "EUR/USD", "disp": "ユーロ/米ドル", "pip_scale": 0.0001}
]

# 後方互換性のためのエイリアス
GMO_PAIRS = SBI_PAIRS
TARGET_PAIRS = SBI_PAIRS


def fetch_forex_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """指定した通貨ペアの価格データを取得"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()


def generate_technical_features(df: pd.DataFrame, pip_scale: float = 0.01) -> pd.DataFrame:
    """テクニカル指標の計算"""
    if df.empty:
        return df
    
    data = df.copy()
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["SMA_200"] = data["Close"].rolling(window=200).mean()
    
    # RSI
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    data["RSI"] = 100 - (100 / (1 + rs))
    
    data.dropna(inplace=True)
    return data


def analyze_all_gmo_pairs(target_pips: float = 250.0) -> list:
    """全10ペアの一括分析"""
    results = []
    for pair in SBI_PAIRS:
        df = fetch_forex_data(pair["symbol"])
        if not df.empty:
            df = generate_technical_features(df, pip_scale=pair["pip_scale"])
            latest_price = df["Close"].iloc[-1]
            results.append({
                "name": pair["name"],
                "display_name": pair["disp"],
                "symbol": pair["symbol"],
                "price": round(float(latest_price), 4),
                "long_prob": 65.0,  # 簡易表示用
                "short_prob": 35.0,
                "rsi": round(float(df["RSI"].iloc[-1]), 1) if "RSI" in df.columns else 50.0,
                "atr_pips": 100.0,
                "data": df
            })
    return results
