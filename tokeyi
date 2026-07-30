import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;

app.use(express.json());

// 家族用アクセス制限・パスコード & 1日上限設定
let familyPin = process.env.FAMILY_PIN || "0516"; // 初期パスコード: 0516
const MAX_DAILY_USERS = 100; // 1日100人/セッション上限

// 日次アクティブユーザー管理 (日付変更時に自動リセット)
let lastResetDate = new Date().toISOString().slice(0, 10);
const dailyActiveUsers = new Set<string>();

function checkAndResetDailyCounter() {
  const currentDate = new Date().toISOString().slice(0, 10);
  if (currentDate !== lastResetDate) {
    dailyActiveUsers.clear();
    lastResetDate = currentDate;
  }
}

// 認証ミドルウェア: トークンなしのAPI直接アクセスをブロック
const requireFamilyAuth = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const authToken = req.headers["x-family-auth-token"];
  if (!authToken || authToken !== `FAMILY_GRANTED_${familyPin}`) {
    return res.status(403).json({
      error: "Access Denied: Unauthenticated external request. This API is strictly private for family use.",
      code: "API_PRIVATE"
    });
  }
  next();
};

// --- APIルート ---

// 利用状況・アクセス制限ステータス取得
app.get("/api/security/stats", (req, res) => {
  checkAndResetDailyCounter();
  const clientIp = (req.headers["x-forwarded-for"] as string)?.split(",")[0] || req.ip || "127.0.0.1";
  
  const isAlreadyRegistered = dailyActiveUsers.has(clientIp);
  const currentCount = dailyActiveUsers.size;
  const isCapReached = currentCount >= MAX_DAILY_USERS && !isAlreadyRegistered;

  res.json({
    dailyUserCount: currentCount,
    maxDailyUsers: MAX_DAILY_USERS,
    isCapReached,
    isAlreadyRegistered,
    apiPublic: false,
    securityLevel: "High (Family Locked + Daily 100 User Limit)",
    resetDate: lastResetDate
  });
});

// パスコード検証 & アクセストークン発行
app.post("/api/auth/verify", (req, res) => {
  checkAndResetDailyCounter();
  const { pin } = req.body;
  const clientIp = (req.headers["x-forwarded-for"] as string)?.split(",")[0] || req.ip || "127.0.0.1";

  if (!pin || pin !== familyPin) {
    return res.status(401).json({
      success: false,
      message: "パスコードが違います。家族専用のパスコードを入力してください。"
    });
  }

  // 1日100人上限チェック
  if (!dailyActiveUsers.has(clientIp) && dailyActiveUsers.size >= MAX_DAILY_USERS) {
    return res.status(429).json({
      success: false,
      message: "本日の家族利用上限（100人/セッション）に達したため、新規アクセスは制限されています。"
    });
  }

  dailyActiveUsers.add(clientIp);

  res.json({
    success: true,
    token: `FAMILY_GRANTED_${familyPin}`,
    message: "家族認証に成功しました。",
    dailyUserCount: dailyActiveUsers.size,
    maxDailyUsers: MAX_DAILY_USERS
  });
});

// パスコード変更 API
app.post("/api/auth/change-pin", requireFamilyAuth, (req, res) => {
  const { currentPin, newPin } = req.body;

  if (currentPin !== familyPin) {
    return res.status(400).json({
      success: false,
      message: "現在のパスコードが正しくありません。"
    });
  }

  if (!newPin || newPin.length < 4) {
    return res.status(400).json({
      success: false,
      message: "新しいパスコードは4桁以上で設定してください。"
    });
  }

  familyPin = newPin;
  res.json({
    success: true,
    newToken: `FAMILY_GRANTED_${familyPin}`,
    message: "パスコードを正常に変更しました。"
  });
});

// 非公開タイマー保護エンドポイント (APIブロック検証用)
app.get("/api/timer/config", requireFamilyAuth, (_req, res) => {
  res.json({
    status: "protected",
    apiScope: "private-family-only"
  });
});

// Vite & 静的ファイル配信
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
    app.get("*", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[Family Security Server] Running on http://localhost:${PORT}`);
  });
}

startServer();
