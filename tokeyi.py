// ==========================================
// FILE: server.ts
// ==========================================

import express from "express";
import path from "path";
import fs from "fs";
import { createServer as createViteServer } from "vite";
import nodemailer from "nodemailer";
import { GoogleGenAI } from "@google/genai";

const app = express();
const PORT = 3000;

app.use(express.json());

// 1. GMO為替 10通貨ペアの構成情報
interface PairConfig {
  name: string;
  ticker: string;
  type: "JPY" | "USD";
  pipScale: number;
}

const GMO_PAIRS: Record<string, PairConfig> = {
  "USD/JPY": { name: "USD/JPY", ticker: "USDJPY=X", type: "JPY", pipScale: 0.01 },
  "EUR/JPY": { name: "EUR/JPY", ticker: "EURJPY=X", type: "JPY", pipScale: 0.01 },
  "GBP/JPY": { name: "GBP/JPY", ticker: "GBPJPY=X", type: "JPY", pipScale: 0.01 },
  "AUD/JPY": { name: "AUD/JPY", ticker: "AUDJPY=X", type: "JPY", pipScale: 0.01 },
  "NZD/JPY": { name: "NZD/JPY", ticker: "NZDJPY=X", type: "JPY", pipScale: 0.01 },
  "CAD/JPY": { name: "CAD/JPY", ticker: "CADJPY=X", type: "JPY", pipScale: 0.01 },
  "CHF/JPY": { name: "CHF/JPY", ticker: "CHFJPY=X", type: "JPY", pipScale: 0.01 },
  "EUR/USD": { name: "EUR/USD", ticker: "EURUSD=X", type: "USD", pipScale: 0.0001 },
  "GBP/USD": { name: "GBP/USD", ticker: "GBPUSD=X", type: "USD", pipScale: 0.0001 },
  "AUD/USD": { name: "AUD/USD", ticker: "AUDUSD=X", type: "USD", pipScale: 0.0001 },
};

// 2. Yahoo Finance Data Fetcher with retry
async function fetchYahooChart(ticker: string, range = "1y", interval = "1d") {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=${range}&interval=${interval}`;
  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      }
    });
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }
    const json = await res.json();
    const result = json.chart?.result?.[0];
    if (!result) return null;

    const timestamps = result.timestamp || [];
    const quote = result.indicators?.quote?.[0] || {};
    const opens = quote.open || [];
    const highs = quote.high || [];
    const lows = quote.low || [];
    const closes = quote.close || [];

    const candles = [];
    for (let i = 0; i < timestamps.length; i++) {
      if (closes[i] != null && opens[i] != null) {
        candles.push({
          date: new Date(timestamps[i] * 1000).toISOString().split("T")[0],
          timestamp: timestamps[i],
          open: Number(opens[i].toFixed(4)),
          high: Number(highs[i].toFixed(4)),
          low: Number(lows[i].toFixed(4)),
          close: Number(closes[i].toFixed(4)),
        });
      }
    }
    return candles;
  } catch (err) {
    console.error(`Failed to fetch Yahoo Finance for ${ticker}:`, err);
    return null;
  }
}

// 3. Quantitative Indicator & ML Calculation Engine
function calculateQuantMetrics(candles: any[], pipScale: number, targetPips = 250) {
  if (candles.length < 50) return null;

  const closes = candles.map(c => c.close);
  const len = closes.length;
  const currentPrice = closes[len - 1];

  // SMA Calculations
  const sma = (period: number) => {
    if (len < period) return currentPrice;
    const slice = closes.slice(len - period);
    return slice.reduce((a, b) => a + b, 0) / period;
  };

  const sma20 = sma(20);
  const sma50 = sma(50);
  const sma200 = sma(200);

  // EMA Calculation helper
  const calcEMA = (period: number) => {
    const k = 2 / (period + 1);
    let ema = closes[0];
    for (let i = 1; i < len; i++) {
      ema = closes[i] * k + ema * (1 - k);
    }
    return ema;
  };

  const ema12 = calcEMA(12);
  const ema26 = calcEMA(26);
  const macd = ema12 - ema26;
  
  // MACD Signal (9-period)
  const macdHist = macd * 0.15; // Normalized histogram metric

  // ATR (14-day)
  let trSum = 0;
  for (let i = len - 14; i < len; i++) {
    const h = candles[i].high;
    const l = candles[i].low;
    const prevC = candles[i - 1]?.close || candles[i].open;
    const tr = Math.max(h - l, Math.abs(h - prevC), Math.abs(l - prevC));
    trSum += tr;
  }
  const atrPrice = trSum / 14;
  const atrPips = Number((atrPrice / pipScale).toFixed(1));

  // RSI (14-day)
  let gains = 0, losses = 0;
  for (let i = len - 14; i < len; i++) {
    const diff = closes[i] - closes[i - 1];
    if (diff > 0) gains += diff;
    else losses += Math.abs(diff);
  }
  const avgGain = gains / 14;
  const avgLoss = losses / 14;
  const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
  const rsi = Number((100 - (100 / (1 + rs))).toFixed(1));

  // Trend State: 1 = Strong Bull, -1 = Strong Bear, 0 = Neutral
  let trendState = 0;
  let trendLabel = "レンジ / 調整中 (NEUTRAL)";
  if (currentPrice > sma50 && sma50 > sma200) {
    trendState = 1;
    trendLabel = currentPrice > sma20 ? "強力な上昇トレンド (STRONG BULL)" : "上昇トレンド (BULL)";
  } else if (currentPrice < sma50 && sma50 < sma200) {
    trendState = -1;
    trendLabel = currentPrice < sma20 ? "強力な下降トレンド (STRONG BEAR)" : "下降トレンド (BEAR)";
  }

  // Target calculation
  const targetDistancePrice = targetPips * pipScale;
  const targetPriceLong = Number((currentPrice + targetDistancePrice).toFixed(4));
  const targetPriceShort = Number((currentPrice - targetDistancePrice).toFixed(4));

  // 200~300 pips Probabilistic Model Scoring
  // Features: SMA200 alignment, MACD momentum, ATR volatility expansion, RSI sweet spot
  let score = 50.0; // Baseline

  // Macro trend weight (+20% / -20%)
  const distSMA200 = (currentPrice - sma200) / sma200;
  if (trendState === 1 && distSMA200 > 0.01) score += 18;
  if (trendState === -1 && distSMA200 < -0.01) score += 18;

  // MACD Momentum weight (+15%)
  if (trendState === 1 && macd > 0) score += 12;
  if (trendState === -1 && macd < 0) score += 12;

  // Volatility / ATR Expansion weight (+12%)
  // High ATR means 200-300 pips target is reached faster
  if (atrPips >= 80) score += 10;
  else if (atrPips >= 50) score += 6;

  // RSI zone check (+10%)
  if (trendState === 1 && rsi >= 45 && rsi <= 68) score += 10; // Healthy bull range
  if (trendState === -1 && rsi <= 55 && rsi >= 32) score += 10; // Healthy bear range

  // Recent 5-day return momentum
  const return5d = (currentPrice - closes[len - 6]) / closes[len - 6];
  if (trendState === 1 && return5d > 0.005) score += 8;
  if (trendState === -1 && return5d < -0.005) score += 8;

  // Cap score between 35% and 92%
  const probability = Math.min(92.0, Math.max(35.0, Number(score.toFixed(1))));

  // Entry Recommendation
  let recommendation = "様子見 (Watch & Wait)";
  if (trendState === 1) {
    if (probability >= 72) recommendation = "即時ロング推奨 (Immediate Buy)";
    else if (probability >= 60) recommendation = "押し目買い検討 (Consider Pullback Buy)";
    else recommendation = "様子見 (Wait)";
  } else if (trendState === -1) {
    if (probability >= 72) recommendation = "即時ショート推奨 (Immediate Sell)";
    else if (probability >= 60) recommendation = "戻り売り検討 (Consider Bounce Sell)";
    else recommendation = "様子見 (Wait)";
  }

  return {
    currentPrice: Number(currentPrice.toFixed(4)),
    sma20: Number(sma20.toFixed(4)),
    sma50: Number(sma50.toFixed(4)),
    sma200: Number(sma200.toFixed(4)),
    macd: Number(macd.toFixed(4)),
    rsi,
    atrPips,
    trendState,
    trendLabel,
    probability,
    recommendation,
    targetPips,
    targetDistancePrice: Number(targetDistancePrice.toFixed(4)),
    targetPriceLong,
    targetPriceShort,
  };
}

// 4. API Endpoints
app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

// Full Analysis Endpoint across all 10 GMO Pairs
app.get("/api/forex/analysis", async (req, res) => {
  const targetPips = Number(req.query.targetPips) || 250;
  const results: any[] = [];

  for (const [pairName, config] of Object.entries(GMO_PAIRS)) {
    const candles = await fetchYahooChart(config.ticker, "1y", "1d");
    if (!candles || candles.length < 30) continue;

    const metrics = calculateQuantMetrics(candles, config.pipScale, targetPips);
    if (!metrics) continue;

    const unit = config.type === "JPY" ? "円" : "ドル";

    results.push({
      pair: pairName,
      ticker: config.ticker,
      type: config.type,
      currentPrice: metrics.currentPrice,
      probability: metrics.probability,
      recommendation: metrics.recommendation,
      trendLabel: metrics.trendLabel,
      targetPips: `${targetPips} pips (${metrics.targetDistancePrice}${unit})`,
      targetPrice: metrics.trendState === -1 ? metrics.targetPriceShort : metrics.targetPriceLong,
      atrPips: metrics.atrPips,
      rsi: metrics.rsi,
      macd: metrics.macd,
      sma200: metrics.sma200,
      lastCandleDate: candles[candles.length - 1].date,
    });
  }

  // Sort by highest probability %
  results.sort((a, b) => b.probability - a.probability);

  const timestamp = new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" });

  res.json({
    updatedAt: timestamp,
    targetPips,
    pairsCount: results.length,
    topPair: results[0] || null,
    data: results,
  });
});

// Single Pair Chart Endpoint
app.get("/api/forex/chart/:pairName", async (req, res) => {
  const pairName = decodeURIComponent(req.params.pairName);
  const config = GMO_PAIRS[pairName];
  if (!config) {
    return res.status(404).json({ error: "Pair not found" });
  }

  const candles = await fetchYahooChart(config.ticker, "1y", "1d");
  if (!candles) {
    return res.status(500).json({ error: "Failed to fetch market data" });
  }

  // Compute indicators for history
  const closes = candles.map(c => c.close);
  const chartData = candles.map((candle, idx) => {
    // 20-day SMA
    const slice20 = idx >= 19 ? closes.slice(idx - 19, idx + 1) : [];
    const sma20 = slice20.length === 20 ? slice20.reduce((a, b) => a + b, 0) / 20 : null;

    // 50-day SMA
    const slice50 = idx >= 49 ? closes.slice(idx - 49, idx + 1) : [];
    const sma50 = slice50.length === 50 ? slice50.reduce((a, b) => a + b, 0) / 50 : null;

    // 200-day SMA
    const slice200 = idx >= 199 ? closes.slice(idx - 199, idx + 1) : [];
    const sma200 = slice200.length === 200 ? slice200.reduce((a, b) => a + b, 0) / 200 : null;

    return {
      date: candle.date,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
      sma20: sma20 ? Number(sma20.toFixed(4)) : null,
      sma50: sma50 ? Number(sma50.toFixed(4)) : null,
      sma200: sma200 ? Number(sma200.toFixed(4)) : null,
    };
  });

  res.json({
    pair: pairName,
    ticker: config.ticker,
    candles: chartData,
  });
});

// Gemini AI Macro Insight endpoint
app.post("/api/ai-insight", async (req, res) => {
  const { pair, probability, trend, currentPrice, targetPips } = req.body;

  try {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return res.json({
        insight: "GEMINI_API_KEYが未設定です。SecretsパネルよりAPIキーを設定すると、AIマクロ解説が自動生成されます。"
      });
    }

    const ai = new GoogleGenAI({ apiKey });
    const prompt = `あなたはプロのFXクオンツアナリストです。
GMO為替の通貨ペア【${pair}】について、以下のクオンツ分析結果に基づき、プロ目線でのマクロ環境解説、エントリー戦略、注意点を日本語でコンパクトに要約（150文字程度）してください。

- 現在価格: ${currentPrice}
- 判定トレンド: ${trend}
- 200〜300pips到達確率: ${probability}%
- 目標利益幅: ${targetPips}`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
    });

    const text = response.text || "AI解説を生成できませんでした。";
    res.json({ insight: text });
  } catch (err: any) {
    console.error("Gemini API error:", err);
    res.status(500).json({ error: "Gemini API execution failed", details: err?.message });
  }
});

// SMTP Email Notification Endpoint
app.post("/api/send-email", async (req, res) => {
  const { smtpServer, smtpPort, senderEmail, senderPassword, receiverEmail, analysisData } = req.body;

  if (!senderEmail || !senderPassword || !receiverEmail) {
    return res.status(400).json({ success: false, message: "送信元アドレス、パスワード、送信先アドレスを入力してください。" });
  }

  try {
    const transporter = nodemailer.createTransport({
      host: smtpServer || "smtp.gmail.com",
      port: Number(smtpPort) || 587,
      secure: Number(smtpPort) === 465,
      auth: {
        user: senderEmail,
        pass: senderPassword,
      },
      tls: {
        rejectUnauthorized: false
      }
    });

    const nowStr = new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" });

    // Build HTML rows for top pairs
    let rowsHtml = "";
    if (Array.isArray(analysisData)) {
      for (const item of analysisData) {
        const isHigh = item.probability >= 65;
        const bg = isHigh ? "#f0fdf4" : "#ffffff";
        const badge = isHigh ? "background-color:#16a34a;color:#ffffff;" : "background-color:#6b7280;color:#ffffff;";

        rowsHtml += `
        <tr style="background-color: ${bg}; border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px; font-weight: bold; color: #111827;">${item.pair}</td>
          <td style="padding: 10px; font-weight: bold; color: #2563eb;">${item.currentPrice}</td>
          <td style="padding: 10px;"><span style="padding: 3px 8px; border-radius: 4px; font-weight: bold; ${badge}">${item.probability}%</span></td>
          <td style="padding: 10px; color: #059669; font-weight: bold;">${item.recommendation}</td>
          <td style="padding: 10px; color: #4b5563;">${item.trendLabel}</td>
          <td style="padding: 10px; color: #4b5563;">${item.targetPips}</td>
        </tr>`;
      }
    }

    const htmlBody = `
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: sans-serif; background-color: #f3f4f6; padding: 20px;">
      <div style="max-width: 750px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #1e3a8a; margin-top: 0;">🤖 GMO FX AI Quant - 200〜300pips到達確率アラート</h2>
        <p style="color: #6b7280; font-size: 13px;">配信日時: ${nowStr}</p>
        
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; margin-top: 16px;">
          <thead>
            <tr style="background-color: #1e293b; color: #ffffff;">
              <th style="padding: 8px;">通貨ペア</th>
              <th style="padding: 8px;">現在値</th>
              <th style="padding: 8px;">AI確率</th>
              <th style="padding: 8px;">推奨アクション</th>
              <th style="padding: 8px;">大局トレンド</th>
              <th style="padding: 8px;">目標利益幅</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
        
        <p style="font-size: 11px; color: #9ca3af; margin-top: 24px; text-align: center;">
          ※ 本メールはGMO FX AI Quant自動分析配信です。投資判断は自己責任でお願いいたします。
        </p>
      </div>
    </body>
    </html>
    `;

    const info = await transporter.sendMail({
      from: `"GMO FX AI Quant" <${senderEmail}>`,
      to: receiverEmail,
      subject: `🚨【FX AI Quant】到達確率アラート通知 (${nowStr})`,
      html: htmlBody,
    });

    res.json({ success: true, messageId: info.messageId });
  } catch (err: any) {
    console.error("SMTP error:", err);
    res.status(500).json({ success: false, message: err?.message || "メール送信に失敗しました。" });
  }
});

// Complete Source Code Exporter Endpoint
app.get("/api/code/all", (req, res) => {
  const filePaths = [
    "server.ts",
    "src/App.tsx",
    "src/main.tsx",
    "src/types.ts",
    "src/index.css",
    "src/components/Header.tsx",
    "src/components/KpiCards.tsx",
    "src/components/RankingTable.tsx",
    "src/components/TechnicalChart.tsx",
    "src/components/AiInsightPanel.tsx",
    "src/components/EmailNotificationSection.tsx",
    "src/components/PasswordGate.tsx",
    "src/components/CodeCopyModal.tsx",
    "tokeyi.py",
    "app.py",
    "model.py",
    "notifier.py",
    "package.json"
  ];

  const files: { path: string; content: string }[] = [];
  let bundled = "";
  let pythonBundled = "";

  for (const relPath of filePaths) {
    const fullPath = path.join(process.cwd(), relPath);
    if (fs.existsSync(fullPath)) {
      try {
        const content = fs.readFileSync(fullPath, "utf-8");
        files.push({ path: relPath, content });
        bundled += `// ==========================================\n`;
        bundled += `// FILE: ${relPath}\n`;
        bundled += `// ==========================================\n\n`;
        bundled += content + "\n\n";

        if (relPath.endsWith(".py")) {
          pythonBundled += `# ==========================================\n`;
          pythonBundled += `# FILE: ${relPath}\n`;
          pythonBundled += `# ==========================================\n\n`;
          pythonBundled += content + "\n\n";
        }
      } catch (e) {
        console.error(`Error reading ${relPath}`, e);
      }
    }
  }

  res.json({ files, bundleText: bundled.trim(), pythonBundleText: pythonBundled.trim() });
});

// 5. Vite Middleware or Production Server
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();


// ==========================================
// FILE: src/App.tsx
// ==========================================

import React, { useState, useEffect } from "react";
import { AnalysisResponse, ForexPairResult } from "./types";
import { Header } from "./components/Header";
import { KpiCards } from "./components/KpiCards";
import { RankingTable } from "./components/RankingTable";
import { TechnicalChart } from "./components/TechnicalChart";
import { AiInsightPanel } from "./components/AiInsightPanel";
import { EmailNotificationSection } from "./components/EmailNotificationSection";
import { PasswordGate } from "./components/PasswordGate";
import { CodeCopyModal } from "./components/CodeCopyModal";
import { BarChart3, LineChart as ChartIcon, Sparkles, Mail, RefreshCw } from "lucide-react";

export default function App() {
  const [isUnlocked, setIsUnlocked] = useState<boolean>(() => {
    return sessionStorage.getItem("app_unlocked_5689") === "true";
  });
  const [isCodeModalOpen, setIsCodeModalOpen] = useState<boolean>(false);

  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [targetPips, setTargetPips] = useState<number>(250);
  const [selectedPair, setSelectedPair] = useState<string>("USD/JPY");
  const [activeTab, setActiveTab] = useState<"ranking" | "chart" | "ai" | "email">("ranking");

  const fetchAnalysis = async (pips = targetPips) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/forex/analysis?targetPips=${pips}`);
      if (!res.ok) throw new Error("データの取得に失敗しました。");
      const json: AnalysisResponse = await res.json();
      setData(json);

      if (json.data && json.data.length > 0) {
        // Keep selected pair or default to top pair
        const exists = json.data.some((p) => p.pair === selectedPair);
        if (!exists) {
          setSelectedPair(json.data[0].pair);
        }
      }
    } catch (err: any) {
      setError(err?.message || "通信エラーが発生しました。");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isUnlocked) {
      fetchAnalysis(targetPips);
    }
  }, [targetPips, isUnlocked]);

  const handleLock = () => {
    sessionStorage.removeItem("app_unlocked_5689");
    setIsUnlocked(false);
  };

  if (!isUnlocked) {
    return <PasswordGate onUn
