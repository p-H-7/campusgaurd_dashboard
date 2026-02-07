import time
import requests
import streamlit as st
from datetime import datetime
from typing import Dict, List

API_BASE = st.secrets.get("API_BASE", "http://localhost:8787")
TOKEN = st.secrets.get("CAMPUSGUARD_TOKEN", "demo-token")

st.set_page_config(page_title="CampusGuard Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
.threat-critical { background-color: #ff4444; color: white; padding: 10px; border-radius: 5px; }
.threat-high { background-color: #ff8800; color: white; padding: 10px; border-radius: 5px; }
.threat-medium { background-color: #ffaa00; color: black; padding: 10px; border-radius: 5px; }
.threat-low { background-color: #44ff44; color: black; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ CampusGuard AI-Powered Security Dashboard")

# Sidebar
with st.sidebar:
    st.header("⚙️ NPU LLM Settings")
    analysis_interval = st.slider("Analysis Interval (seconds)", 10, 120, 30)
    lookback_minutes = st.slider("Analyze last N minutes", 5, 60, 15)
    
    st.divider()
    st.header("📊 Alert Settings")
    limit = st.number_input("Alerts to show", min_value=5, max_value=200, value=30, step=5)
    refresh_s = st.number_input("Refresh (seconds)", min_value=1, max_value=30, value=2, step=1)
    
    st.divider()
    st.header("🖥️ NPU Status")
    
    # Initialize and check NPU
    try:
        from npu_llm_engine import get_npu_engine
        engine = get_npu_engine()
        
        provider = engine.session.get_providers()[0]
        if provider == 'DmlExecutionProvider':
            st.success("✅ Snapdragon X Elite NPU Active")
        else:
            st.error(f"❌ NPU not active! Using: {provider}")
            
    except Exception as e:
        st.error(f"❌ NPU LLM Error:\n{str(e)}")
        st.stop()

def fetch_alerts():
    r = requests.get(
        f"{API_BASE}/alerts",
        params={"limit": int(limit)},
        headers={"x-campusguard-token": TOKEN},
        timeout=3,
    )
    r.raise_for_status()
    return r.json()["alerts"]

def analyze_alerts_with_npu(alerts: List[Dict]) -> Dict:
    """
    Analyze alerts using NPU LLM - NO FALLBACK
    """
    if not alerts:
        return {
            "threat_level": "LOW",
            "summary": "No recent alerts to analyze.",
            "recommendations": ["Continue routine monitoring"],
            "alert_security": False,
            "npu_processed": True
        }
    
    # Filter recent alerts
    cutoff_time = time.time() * 1000 - (lookback_minutes * 60 * 1000)
    recent_alerts = [a for a in alerts if a["ts"] > cutoff_time]
    
    if not recent_alerts:
        return {
            "threat_level": "LOW",
            "summary": f"No alerts in the last {lookback_minutes} minutes.",
            "recommendations": ["Continue routine monitoring"],
            "alert_security": False,
            "npu_processed": True
        }
    
    # Prepare alert summary
    alert_summary = []
    for a in recent_alerts:
        ts = datetime.fromtimestamp(a["ts"] / 1000.0).strftime("%H:%M:%S")
        verdict = a.get("operatorVerdict", "UNKNOWN")
        event = a["eventType"]
        conf = a.get("modelConfidence", 0)
        device = a.get("deviceId", "unknown")
        
        alert_summary.append(
            f"- {ts} | {event} | Verdict: {verdict} | "
            f"Confidence: {conf:.2f} | Device: {device}"
        )
    
    alert_text = "\n".join(alert_summary)
    
    # Count alert types
    yes_count = sum(1 for a in recent_alerts if a.get("operatorVerdict") == "YES")
    maybe_count = sum(1 for a in recent_alerts if a.get("operatorVerdict") == "MAYBE")
    
    # Run NPU analysis
    from npu_llm_engine import get_npu_engine
    npu_engine = get_npu_engine()
    
    analysis = npu_engine.analyze_alerts(
        alert_text, 
        yes_count, 
        maybe_count, 
        len(recent_alerts),
        lookback_minutes
    )
    
    return analysis

# Main layout
col1, col2 = st.columns([2, 1])

with col2:
    st.header("🤖 NPU AI Analysis")
    analysis_placeholder = st.empty()

with col1:
    st.header("📋 Recent Alerts")
    alerts_placeholder = st.empty()

# Session state
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = 0
if 'cached_analysis' not in st.session_state:
    st.session_state.cached_analysis = None

# Main loop
while True:
    try:
        alerts = fetch_alerts()
    except Exception as e:
        st.error(f"Failed to fetch alerts: {e}")
        time.sleep(refresh_s)
        continue

    # Display alerts
    with alerts_placeholder.container():
        if not alerts:
            st.info("No alerts yet.")
        else:
            for a in alerts:
                ts = datetime.fromtimestamp(a["ts"] / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
                verdict = a.get("operatorVerdict", "UNKNOWN")
                conf = a.get("modelConfidence", None)
                device = a.get("deviceId", "unknown")

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
                        try:
                            st.image(f"{API_BASE}/images/{img}", caption="Captured frame", use_container_width=True)
                        except:
                            pass

    # NPU Analysis
    current_time = time.time()
    if (current_time - st.session_state.last_analysis_time) >= analysis_interval:
        st.session_state.last_analysis_time = current_time
        
        with analysis_placeholder.container():
            with st.spinner("🧠 Snapdragon X Elite NPU analyzing alerts..."):
                try:
                    analysis = analyze_alerts_with_npu(alerts)
                    st.session_state.cached_analysis = analysis
                except Exception as e:
                    st.error(f"❌ NPU Analysis Failed:\n{str(e)}")
                    st.stop()
            
            # Display results
            threat_level = analysis["threat_level"]
            threat_class = f"threat-{threat_level.lower()}"
            
            st.markdown(f'<div class="{threat_class}"><h2>🎯 {threat_level}</h2></div>', unsafe_allow_html=True)
            st.success("⚡ Powered by Snapdragon X Elite NPU")
            
            st.write("### 📊 Assessment")
            st.write(analysis["summary"])
            
            st.write("### 📋 Actions")
            for i, rec in enumerate(analysis["recommendations"], 1):
                st.write(f"{i}. {rec}")
            
            if analysis["alert_security"]:
                st.error("🚨 **SECURITY ALERT**")
            
            st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    elif st.session_state.cached_analysis:
        # Show cached
        with analysis_placeholder.container():
            analysis = st.session_state.cached_analysis
            threat_level = analysis["threat_level"]
            threat_class = f"threat-{threat_level.lower()}"
            
            st.markdown(f'<div class="{threat_class}"><h2>🎯 {threat_level}</h2></div>', unsafe_allow_html=True)
            st.success("⚡ Snapdragon X Elite NPU")
            
            st.write("### 📊 Assessment")
            st.write(analysis["summary"])
            
            st.write("### 📋 Actions")
            for i, rec in enumerate(analysis["recommendations"], 1):
                st.write(f"{i}. {rec}")
            
            next_update = analysis_interval - (current_time - st.session_state.last_analysis_time)
            st.caption(f"Next update: {int(next_update)}s")

    time.sleep(refresh_s)