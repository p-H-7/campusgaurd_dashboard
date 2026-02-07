# 🛡️ **CampusGuard-Demo**

A real-time, human-in-the-loop campus safety monitoring system that combines **on-device AI**, **operator validation**, and a **live security dashboard**.

This project was built for a hackathon/demo setting to showcase:

* Edge AI (on Android) for anomaly detection
* Real-time alerts with evidence (camera frame)
* A simple but functional security dashboard for campus personnel

---

## 🎯 **What CampusGuard Does**

CampusGuard continuously analyzes camera footage on a mobile device and detects potentially suspicious or dangerous situations such as:

* 🔪 **Knife detection**
* 🧍 **Person down / lying position**
* 🏃 **Rapid movement (running)**
* 👥 **Other person-based anomalies**

When the AI flags something as suspicious, the operator (security guard or user) can confirm it via a simple UI:

* **YES (Definitely suspicious)**
* **MAYBE (Not sure)**
* **NO (Ignore)**

If YES or MAYBE is selected, an alert (with a screenshot) is sent to a **live security dashboard**.

---

## 🏗️ **System Architecture**

```
Android App  -->  Node Alert Server  -->  Streamlit Dashboard
(Edge AI + UI)      (Stores alerts)       (Live visualization)
```

### Component Breakdown

### 📱 1) Android App (`android-app/`)

Responsibilities:

* Runs YOLOv8 ONNX model on-device using **ONNX Runtime**
* Detects:

  * Person-based anomalies
  * Knife (COCO class 43)
* Shows a confirmation popup when something suspicious is detected
* Sends:

  * Event type (e.g., "Knife Detected")
  * Model confidence
  * Operator verdict (YES/MAYBE)
  * Screenshot of the frame

**Key files:**

* `InferenceEngine.kt` → AI model inference + knife detection
* `CameraScreen.kt` → Camera feed + alert UI + sending alerts
* `AlertSender.kt` → HTTP client that sends alerts to server

---

### 🖥️ 2) Alert Server (`server/`)

A lightweight **Node.js + TypeScript** backend that:

* Receives alerts from the phone via HTTP POST
* Stores:

  * Event metadata in memory (for demo)
  * Screenshot images on disk
* Exposes:

  * `POST /alert` → receive new alerts
  * `GET /alerts` → return latest alerts
  * `GET /images/{id}.jpg` → serve captured frames
  * `GET /health` → server status check

**Tech stack:** Express, TypeScript

---

### 📊 3) Security Dashboard (`dashboard/`)

A **Streamlit (Python) web app** that:

* Polls the Node server every few seconds
* Displays alerts as cards with:

  * Event type
  * Confidence score
  * Operator verdict (YES/MAYBE)
  * Timestamp
  * Captured frame from phone

**Tech stack:** Streamlit, Python, Requests

---

## 📁 **Project Structure**

```
CampusGuard-Demo/
│
├── android-app/
│   └── (Full Android Studio project)
│
├── server/
│   ├── src/index.ts
│   ├── data/images/
│   ├── package.json
│   └── tsconfig.json
│
├── dashboard/
│   ├── app.py
│   └── .streamlit/secrets.toml
│
└── README.md   ← (this file)
```

---

# 🚀 **HOW TO RUN EVERYTHING (DEMO DAY)**

## ✅ **Step 1 — Run the Node Alert Server (IMPORTANT)**

### **First time only — install dependencies**

From the `server/` folder:

```bash
cd server
npm install
```

### **Start the server**

#### **On Mac / Linux**

```bash
CAMPUSGUARD_TOKEN=demo-token npm run dev
```

#### **On Windows (PowerShell) — Recommended**

Run this **once**:

```powershell
setx CAMPUSGUARD_TOKEN "demo-token"
```

👉 Close and reopen the terminal, then run:

```powershell
cd CampusGuard-Demo/server
npm run dev
```

> (If you don’t want to set the variable, you can just run `npm run dev` — the server defaults to `demo-token`.)

You should see:

```
✅ Alert server running on http://localhost:8787
Token header: x-campusguard-token = demo-token
```

### **Check server health**

Open in browser:

```
http://localhost:8787/health
```

You should see:

```json
{"ok": true}
```

### **Check from phone (real device)**

If your laptop IP is `10.206.138.203`, open on your phone:

```
http://10.206.138.203:8787/health
```

If this works → your phone can talk to the server.

---

## ✅ **Step 2 — Run the Streamlit Dashboard**

From the `dashboard/` folder:

```bash
cd dashboard
streamlit run app.py
```

Open:

```
http://localhost:8501
```

---

## ✅ **Step 3 — Run the Android App**

* Connect a real Android phone (recommended for demo)
* Make sure phone and laptop are on the **same Wi-Fi**
* In `CameraScreen.kt`, set:

```kotlin
apiBase = "http://<YOUR_LAPTOP_IP>:8787"
```

Example:

```kotlin
apiBase = "http://10.206.138.203:8787"
```

---

## ✅ **Step 4 — End-to-End Test**

1. Trigger a knife or anomaly detection in the app
2. Tap **YES** or **MAYBE**
3. The alert should appear **instantly** on the dashboard with a screenshot 🎉

---

## 🔐 Security (Demo-Level)

This system uses a simple header-based token:

```
x-campusguard-token: demo-token
```

⚠️ This is **not production-grade security** — it’s for demo/hackathon purposes only.

---

## 🧠 AI Model Notes

* Uses **YOLOv8 ONNX** for on-device inference
* Knife detection relies on **COCO class index 43**
* If your model is “person-only”, knife detection will **not work**
* Frame processing is throttled (every 15 frames) to keep the app smooth

---

## ⚠️ Limitations (Honest Demo Notes)

This is a **proof-of-concept**, not a production system:

* Alerts are stored **in memory** (server restarts clear them)
* No user authentication system
* No database
* No long-term logging
* No advanced tracking or multi-object association

---

## 🏁 Hackathon Value Proposition

CampusGuard demonstrates:

* Edge AI + mobile computing
* Real-time security workflow
* Human-in-the-loop decision making
* Cross-platform integration (Android + Web + Server)
* Practical campus safety use case

---

## 👥 Team / Credits

Built for a hackathon as a smart campus security solution using:

* Android (Kotlin + Jetpack Compose)
* ONNX Runtime + YOLOv8
* Node.js + TypeScript
* Streamlit (Python)
