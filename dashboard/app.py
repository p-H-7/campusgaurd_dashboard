import time
import requests
import streamlit as st
from datetime import datetime

API_BASE = st.secrets.get("API_BASE", "http://localhost:8787")
TOKEN = st.secrets.get("CAMPUSGUARD_TOKEN", "demo-token")

st.set_page_config(page_title="CampusGuard Dashboard", layout="wide")
st.title("CampusGuard Security Dashboard")

colA, colB, colC = st.columns([2, 1, 1])
with colA:
    st.caption("Live alerts (demo). Auto-refreshes.")
with colB:
    limit = st.number_input("Alerts to show", min_value=5, max_value=200, value=30, step=5)
with colC:
    refresh_s = st.number_input("Refresh (seconds)", min_value=1, max_value=30, value=2, step=1)

def fetch_alerts():
    r = requests.get(
        f"{API_BASE}/alerts",
        params={"limit": int(limit)},
        headers={"x-campusguard-token": TOKEN},
        timeout=3,
    )
    r.raise_for_status()
    return r.json()["alerts"]

placeholder = st.empty()

while True:
    try:
        alerts = fetch_alerts()
    except Exception as e:
        st.error(f"Failed to fetch alerts: {e}")
        time.sleep(refresh_s)
        continue

    with placeholder.container():
        if not alerts:
            st.info("No alerts yet.")
        else:
            for a in alerts:
                ts = datetime.fromtimestamp(a["ts"] / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
                verdict = a.get("operatorVerdict", "UNKNOWN")
                conf = a.get("modelConfidence", None)
                device = a.get("deviceId", "unknown")

                # Simple severity coloring via emoji
                badge = "🚨" if verdict == "YES" else "⚠️"
                header = f"{badge} {a['eventType']} — {verdict}"

                with st.container(border=True):
                    top = st.columns([3, 1, 1, 2])
                    top[0].subheader(header)
                    top[1].metric("Confidence", f"{conf:.2f}" if isinstance(conf, (int, float)) else "—")
                    top[2].write(f"**Device:** {device}")
                    top[3].write(f"**Time:** {ts}")

                    notes = a.get("notes")
                    if notes:
                        st.write(f"**Notes:** {notes}")

                    img = a.get("imageFile")
                    if img:
                        st.image(f"{API_BASE}/images/{img}", caption="Captured frame", use_container_width=True)

    time.sleep(refresh_s)
