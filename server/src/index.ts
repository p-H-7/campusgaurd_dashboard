import express from "express";
import cors from "cors";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";
import path from "path";

const app = express();
app.use(cors());
app.use(express.json({ limit: "15mb" })); // allow base64 images

const PORT = process.env.PORT ? Number(process.env.PORT) : 8787;
const AUTH_TOKEN = process.env.CAMPUSGUARD_TOKEN || "demo-token";

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), "data");
const IMG_DIR = path.join(DATA_DIR, "images");
fs.mkdirSync(IMG_DIR, { recursive: true });

type Alert = {
  id: string;
  ts: number;
  deviceId?: string;
  eventType: string;
  modelConfidence?: number;
  operatorVerdict: "YES" | "MAYBE";
  notes?: string;
  imageFile?: string;
};

const alerts: Alert[] = [];

function requireAuth(req: express.Request, res: express.Response): boolean {
  const token = req.header("x-campusguard-token");
  if (!token || token !== AUTH_TOKEN) {
    res.status(401).json({ error: "Unauthorized" });
    return false;
  }
  return true;
}

// Health check
app.get("/health", (_req, res) => res.json({ ok: true }));

// Receive alert
app.post("/alert", (req, res) => {
  if (!requireAuth(req, res)) return;

  const { eventType, modelConfidence, operatorVerdict, deviceId, notes, imageBase64 } = req.body ?? {};

  if (!eventType || !operatorVerdict) {
    return res.status(400).json({ error: "eventType and operatorVerdict are required" });
  }
  if (operatorVerdict !== "YES" && operatorVerdict !== "MAYBE") {
    return res.status(400).json({ error: "operatorVerdict must be YES or MAYBE" });
  }

  const id = uuidv4();
  const ts = Date.now();

  let imageFile: string | undefined = undefined;
  if (typeof imageBase64 === "string" && imageBase64.length > 0) {
    const base64 = imageBase64.includes(",") ? imageBase64.split(",")[1] : imageBase64;
    const buf = Buffer.from(base64, "base64");
    imageFile = `${id}.jpg`;
    fs.writeFileSync(path.join(IMG_DIR, imageFile), buf);
  }

  const alert: Alert = {
    id,
    ts,
    deviceId,
    eventType,
    modelConfidence: typeof modelConfidence === "number" ? modelConfidence : undefined,
    operatorVerdict,
    notes,
    imageFile
  };

  alerts.unshift(alert);
  if (alerts.length > 200) alerts.length = 200;

  res.json({ ok: true, id });
});

// List alerts
app.get("/alerts", (req, res) => {
  if (!requireAuth(req, res)) return;

  const limit = Math.min(Number(req.query.limit || 50), 200);
  res.json({ alerts: alerts.slice(0, limit) });
});

// Serve images
app.use("/images", express.static(IMG_DIR));

// Optional: make / show something
app.get("/", (_req, res) => res.send("CampusGuard Alert Server running. Try /health"));

app.listen(PORT, () => {
  console.log(`✅ Alert server running on http://localhost:${PORT}`);
  console.log(`Token header: x-campusguard-token = ${AUTH_TOKEN}`);
});
