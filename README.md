# 📊 CampusGuard Security Dashboard

This is a **Streamlit-based live dashboard** for the CampusGuard system. It allows campus security personnel to receive and visualize real-time alerts from the Android app, including:

* Type of detected event (e.g., *Knife Detected*, *Person Down*, etc.)
* Model confidence score
* Operator verdict from the phone (**YES / MAYBE**)
* Timestamp of the alert
* Captured camera frame (screengrab) from the phone

---

## 🔧 Architecture (High Level)

```
Android App  -->  Node Alert Server  -->  Streamlit Dashboard
(button press)      (stores alerts)       (polls & displays)
```

* The **Android app** sends alerts (JSON + Base64 image) when the operator presses a button.
* The **Node/TypeScript server** receives and stores alerts and images.
* The **Streamlit dashboard** polls the server and displays the latest alerts.

---

## 🚀 Setup & Running the Dashboard

### 1️⃣ Install dependencies

From the `dashboard/` folder:

```bash
pip install streamlit requests
```

---

### 2️⃣ Create Streamlit secrets

Create a folder:

```
dashboard/.streamlit/
```

Inside it, create a file:

```
dashboard/.streamlit/secrets.toml
```

Add:

```toml
API_BASE = "http://localhost:8787"
CAMPUSGUARD_TOKEN = "demo-token"
```

> 🔹 **Note:**
>
> * `API_BASE` should point to your Node server.
> * Use `localhost` if running Streamlit on the same laptop as the server.

---

### 3️⃣ Run the dashboard

From the `dashboard/` directory:

```bash
streamlit run app.py
```

The dashboard will open in your browser at:

```
http://localhost:8501
```

---

## 🖥️ What You’ll See

Each alert appears as a card containing:

* 🚨 **Event Type** – What the model detected
* 📱 **Device ID** – Which phone sent the alert
* ⏱️ **Timestamp** – When it happened
* 🎯 **Confidence** – Model confidence score
* ✅ **Operator Verdict** – YES / MAYBE
* 🖼️ **Captured Frame** – Screenshot from the phone (if available)

Alerts auto-refresh every few seconds.

---

## ⚙️ Configuration Options (in UI)

On the dashboard you can adjust:

* **Number of alerts to show**
* **Refresh interval (seconds)**

---

## 📡 Server Dependency

This dashboard requires the **CampusGuard Alert Server** (Node/TypeScript) to be running at:

```
http://localhost:8787
```

To check if the server is alive, visit:

```
http://localhost:8787/health
```

You should see:

```json
{"ok":true}
```

---

## 📱 Phone → Dashboard Flow

1. AI model detects anomaly on phone
2. Operator presses **YES** or **MAYBE**
3. Phone sends:

   * Event type
   * Confidence
   * Verdict
   * Screenshot
4. Dashboard receives and displays the alert instantly

---