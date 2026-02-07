import time
import requests
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

API_BASE = st.secrets.get("API_BASE", "http://localhost:8787")
TOKEN = st.secrets.get("CAMPUSGUARD_TOKEN", "demo-token")

st.set_page_config(
    page_title="CampusGuard Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Color Scheme
COLORS = {
    'primary': '#6366f1',      # Indigo
    'secondary': '#8b5cf6',    # Purple
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Amber
    'danger': '#ef4444',       # Red
    'critical': '#dc2626',     # Dark Red
    'info': '#3b82f6',         # Blue
    'dark': '#1f2937',         # Dark Gray
    'light': '#f3f4f6',        # Light Gray
    'bg_card': '#ffffff',
    'border': '#e5e7eb'
}

# Enhanced Custom CSS
st.markdown(f"""
<style>
    /* Main theme */
    .main {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }}
    
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Custom cards */
    .metric-card {{
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 5px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 2px solid {COLORS['primary']};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS['dark']};
        margin: 0;
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }}
    
    .metric-delta {{
        font-size: 0.875rem;
        margin-top: 8px;
        font-weight: 600;
    }}
    
    /* Alert cards */
    .alert-card {{
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid;
        transition: all 0.2s;
    }}
    
    .alert-card:hover {{
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }}
    
    .alert-critical {{ border-left-color: {COLORS['critical']}; }}
    .alert-high {{ border-left-color: {COLORS['danger']}; }}
    .alert-medium {{ border-left-color: {COLORS['warning']}; }}
    .alert-low {{ border-left-color: {COLORS['success']}; }}
    
    /* Threat level badges */
    .threat-badge {{
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .threat-critical {{
        background: linear-gradient(135deg, {COLORS['critical']} 0%, #991b1b 100%);
        color: white;
    }}
    
    .threat-high {{
        background: linear-gradient(135deg, {COLORS['danger']} 0%, #dc2626 100%);
        color: white;
    }}
    
    .threat-medium {{
        background: linear-gradient(135deg, {COLORS['warning']} 0%, #d97706 100%);
        color: white;
    }}
    
    .threat-low {{
        background: linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%);
        color: white;
    }}
    
    /* Status indicator */
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
    }}
    
    .status-active {{ background-color: {COLORS['success']}; }}
    .status-inactive {{ background-color: {COLORS['danger']}; }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    /* Analysis card */
    .analysis-card {{
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
    }}
    
    .recommendation-item {{
        background: {COLORS['light']};
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 3px solid {COLORS['primary']};
    }}
    
    /* Progress bar */
    .confidence-bar {{
        width: 100%;
        height: 8px;
        background-color: {COLORS['light']};
        border-radius: 4px;
        overflow: hidden;
        margin-top: 4px;
    }}
    
    .confidence-fill {{
        height: 100%;
        background: linear-gradient(90deg, {COLORS['success']} 0%, {COLORS['primary']} 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }}
    
    /* Headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 16px;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 4px;
        border-radius: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        color: {COLORS['primary']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Title with live status
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<h1 style="color: white; margin: 0;">🛡️ CampusGuard AI Security</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgba(255,255,255,0.8); margin-top: 8px;">Real-time AI-Powered Campus Monitoring</p>', unsafe_allow_html=True)

with col_status:
    try:
        from npu_llm_engine import get_npu_engine
        engine = get_npu_engine()
        provider = engine.session.get_providers()[0]
        
        if provider == 'DmlExecutionProvider':
            st.markdown(
                '<div style="background: white; padding: 12px; border-radius: 8px; text-align: center;">'
                '<span class="status-indicator status-active"></span>'
                '<span style="color: #10b981; font-weight: 600;">NPU ACTIVE</span>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="background: white; padding: 12px; border-radius: 8px; text-align: center;">'
                '<span class="status-indicator status-inactive"></span>'
                '<span style="color: #ef4444; font-weight: 600;">NPU INACTIVE</span>'
                '</div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"NPU Error: {str(e)}")
        st.stop()

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    st.markdown("**NPU Analysis**")
    analysis_interval = st.slider("Analysis Interval (sec)", 10, 120, 30)
    lookback_minutes = st.slider("Lookback Window (min)", 5, 60, 15)
    
    st.divider()
    
    st.markdown("**Display Settings**")
    limit = st.number_input("Max Alerts", min_value=5, max_value=200, value=30, step=5)
    refresh_s = st.number_input("Refresh Rate (sec)", min_value=1, max_value=30, value=2, step=1)
    
    st.divider()
    
    st.markdown("**Filter Options**")
    filter_verdict = st.multiselect(
        "Verdict Filter",
        options=["YES", "MAYBE", "NO", "UNKNOWN"],
        default=["YES", "MAYBE", "NO", "UNKNOWN"]
    )
    
    filter_device = st.text_input("Device ID Filter (optional)", "")
    
    st.divider()
    
    st.markdown("**About**")
    st.caption("CampusGuard v2.0")
    st.caption("Powered by Snapdragon X Elite")
    st.caption("© 2024 All Rights Reserved")

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
    """Analyze alerts using NPU LLM"""
    if not alerts:
        return {
            "threat_level": "LOW",
            "summary": "No recent alerts to analyze.",
            "recommendations": ["Continue routine monitoring"],
            "alert_security": False,
            "npu_processed": True
        }
    
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
    
    yes_count = sum(1 for a in recent_alerts if a.get("operatorVerdict") == "YES")
    maybe_count = sum(1 for a in recent_alerts if a.get("operatorVerdict") == "MAYBE")
    
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

def create_threat_timeline(alerts: List[Dict]):
    """Create timeline visualization of threats"""
    if not alerts:
        return None
    
    times = [datetime.fromtimestamp(a["ts"] / 1000.0) for a in alerts]
    verdicts = [a.get("operatorVerdict", "UNKNOWN") for a in alerts]
    confidences = [a.get("modelConfidence", 0) for a in alerts]
    
    color_map = {
        "YES": COLORS['danger'],
        "MAYBE": COLORS['warning'],
        "NO": COLORS['success'],
        "UNKNOWN": COLORS['info']
    }
    
    colors = [color_map.get(v, COLORS['info']) for v in verdicts]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=confidences,
        mode='markers+lines',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=2, color='white')
        ),
        line=dict(color=COLORS['primary'], width=2),
        text=[f"{v}<br>Conf: {c:.2f}" for v, c in zip(verdicts, confidences)],
        hovertemplate='%{text}<br>%{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Threat Timeline",
        xaxis_title="Time",
        yaxis_title="Confidence Score",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['dark']),
        hovermode='closest',
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_verdict_distribution(alerts: List[Dict]):
    """Create verdict distribution pie chart"""
    if not alerts:
        return None
    
    verdicts = [a.get("operatorVerdict", "UNKNOWN") for a in alerts]
    verdict_counts = Counter(verdicts)
    
    fig = go.Figure(data=[go.Pie(
        labels=list(verdict_counts.keys()),
        values=list(verdict_counts.values()),
        marker=dict(colors=[
            COLORS['danger'] if v == "YES" else
            COLORS['warning'] if v == "MAYBE" else
            COLORS['success'] if v == "NO" else
            COLORS['info']
            for v in verdict_counts.keys()
        ]),
        hole=0.4
    )])
    
    fig.update_layout(
        title="Alert Distribution",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['dark']),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    
    return fig

def create_device_activity(alerts: List[Dict]):
    """Create device activity bar chart"""
    if not alerts:
        return None
    
    devices = [a.get("deviceId", "unknown") for a in alerts]
    device_counts = Counter(devices)
    
    fig = go.Figure(data=[go.Bar(
        x=list(device_counts.keys()),
        y=list(device_counts.values()),
        marker=dict(
            color=COLORS['primary'],
            line=dict(color=COLORS['secondary'], width=2)
        )
    )])
    
    fig.update_layout(
        title="Alerts by Device",
        xaxis_title="Device ID",
        yaxis_title="Alert Count",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['dark']),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

# Session state initialization
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = 0
if 'cached_analysis' not in st.session_state:
    st.session_state.cached_analysis = None
if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []

# Fetch and process alerts
try:
    alerts = fetch_alerts()
    
    # Apply filters
    if filter_verdict:
        alerts = [a for a in alerts if a.get("operatorVerdict", "UNKNOWN") in filter_verdict]
    
    if filter_device:
        alerts = [a for a in alerts if filter_device.lower() in a.get("deviceId", "").lower()]
    
except Exception as e:
    st.error(f"❌ Failed to fetch alerts: {e}")
    st.stop()

# Calculate metrics
total_alerts = len(alerts)
threat_alerts = sum(1 for a in alerts if a.get("operatorVerdict") == "YES")
maybe_alerts = sum(1 for a in alerts if a.get("operatorVerdict") == "MAYBE")
avg_confidence = sum(a.get("modelConfidence", 0) for a in alerts) / max(len(alerts), 1)
unique_devices = len(set(a.get("deviceId", "unknown") for a in alerts))

# Main Layout: Top row - Metrics (left) + NPU Analysis (right)
top_row = st.columns([3, 2])

# LEFT COLUMN
with top_row[0]:
    # Metrics in 2 rows
    # First row: Total Alerts, Threats, Uncertain
    metric_row1 = st.columns(3)
    
    with metric_row1[0]:
        st.markdown(
            f'<div class="metric-card">'
            f'<p class="metric-value">{total_alerts}</p>'
            f'<p class="metric-label">Total Alerts</p>'
            f'<p class="metric-delta" style="color: {COLORS["info"]};">Last {lookback_minutes}min</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with metric_row1[1]:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: {COLORS["danger"]}">'
            f'<p class="metric-value">{threat_alerts}</p>'
            f'<p class="metric-label">Threats</p>'
            f'<p class="metric-delta" style="color: {COLORS["danger"]};">⚠️ Active</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with metric_row1[2]:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: {COLORS["warning"]}">'
            f'<p class="metric-value">{maybe_alerts}</p>'
            f'<p class="metric-label">Uncertain</p>'
            f'<p class="metric-delta" style="color: {COLORS["warning"]};">🔍 Review</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Second row: Avg Confidence, Active Devices
    metric_row2 = st.columns([1, 1, 1])
    
    with metric_row2[0]:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: {COLORS["success"]}">'
            f'<p class="metric-value">{avg_confidence:.2f}</p>'
            f'<p class="metric-label">Avg Confidence</p>'
            f'<p class="metric-delta" style="color: {COLORS["success"]};">✓ Score</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with metric_row2[1]:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: {COLORS["primary"]}">'
            f'<p class="metric-value">{unique_devices}</p>'
            f'<p class="metric-label">Active Devices</p>'
            f'<p class="metric-delta" style="color: {COLORS["primary"]};">📡 Online</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alert cards below metrics
    if not alerts:
        st.info("🟢 No alerts detected. System monitoring normally.")
    else:
        st.markdown(f'<p style="color: white; font-weight: 600; margin-bottom: 16px;">📋 Recent Alerts ({min(len(alerts), 15)})</p>', unsafe_allow_html=True)
        
        for idx, a in enumerate(alerts[:15]):
            ts = datetime.fromtimestamp(a["ts"] / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
            verdict = a.get("operatorVerdict", "UNKNOWN")
            conf = a.get("modelConfidence", 0)
            device = a.get("deviceId", "unknown")
            event_type = a["eventType"]
            
            if verdict == "YES":
                badge = "🚨"
                verdict_color = COLORS['danger']
            elif verdict == "MAYBE":
                badge = "⚠️"
                verdict_color = COLORS['warning']
            else:
                badge = "✅"
                verdict_color = COLORS['success']
            
            with st.expander(f"{badge} {event_type} - {verdict} - {ts}", expanded=(idx < 2 and verdict in ["YES", "MAYBE"])):
                info_cols = st.columns([2, 1, 1])
                with info_cols[0]:
                    st.markdown(f"**Event Type:** {event_type}")
                    st.markdown(f"**Device:** {device}")
                with info_cols[1]:
                    st.markdown(f"**Verdict:** `{verdict}`")
                    st.markdown(f"**Time:** {ts.split()[1]}")
                with info_cols[2]:
                    st.metric("Confidence", f"{conf:.2f}")
                
                st.markdown(
                    f'<div class="confidence-bar" style="margin: 12px 0;">'
                    f'<div class="confidence-fill" style="width: {conf*100}%; background: {verdict_color};"></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                notes = a.get("notes")
                if notes:
                    st.info(f"📝 **Notes:** {notes}")
                
                img = a.get("imageFile")
                if img:
                    try:
                        st.image(f"{API_BASE}/images/{img}", caption=f"Captured Frame - {event_type}", use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not load image: {e}")

# RIGHT COLUMN
    with top_row[1]:
        st.markdown('<h2 class="section-header">🤖 NPU AI Analysis</h2>', unsafe_allow_html=True)
        
        current_time = time.time()
        
        if (current_time - st.session_state.last_analysis_time) >= analysis_interval:
            st.session_state.last_analysis_time = current_time
            with st.spinner("🧠 Analyzing with Snapdragon X Elite NPU..."):
                try:
                    analysis = analyze_alerts_with_npu(alerts)
                    st.session_state.cached_analysis = analysis
                except Exception as e:
                    st.error(f"❌ NPU Analysis Failed: {str(e)}")
                    st.stop()
        
        if st.session_state.cached_analysis:
            analysis = st.session_state.cached_analysis
            threat_level = analysis["threat_level"]
            threat_class = f"threat-{threat_level.lower()}"
            
            st.markdown(
                f'<div class="analysis-card">'
                f'<div style="text-align: center; margin-bottom: 20px;">'
                f'<span class="threat-badge {threat_class}" style="font-size: 1.2rem; padding: 12px 24px;">'
                f'🎯 THREAT LEVEL: {threat_level}'
                f'</span>'
                f'</div>'
                f'<div style="background: rgba(99, 102, 241, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">'
                f'<span style="color: {COLORS["primary"]}; font-weight: 600;">⚡ Powered by Snapdragon X Elite NPU</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.markdown("### 📊 Assessment")
            st.markdown(
                f'<div style="background: {COLORS["light"]}; padding: 16px; border-radius: 8px; border-left: 4px solid {COLORS["info"]};">'
                f'{analysis["summary"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 📋 Recommended Actions")
            for i, rec in enumerate(analysis["recommendations"], 1):
                st.markdown(f'<div class="recommendation-item"><strong>{i}.</strong> {rec}</div>', unsafe_allow_html=True)
            
            if analysis.get("alert_security"):
                st.markdown(
                    f'<div style="background: {COLORS["danger"]}; color: white; padding: 16px; border-radius: 8px; margin-top: 16px; text-align: center; font-weight: 600;">'
                    f'🚨 SECURITY ALERT - IMMEDIATE ATTENTION REQUIRED'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            next_update = max(0, analysis_interval - (current_time - st.session_state.last_analysis_time))
            st.markdown(
                f'<div style="text-align: center; margin-top: 20px; color: {COLORS["info"]}; font-size: 0.875rem;">'
                f'Last Updated: {datetime.now().strftime("%H:%M:%S")}<br>'
                f'Next Analysis: {int(next_update)}s'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Live Alert Feed</h2>', unsafe_allow_html=True)
        
        timeline_fig = create_threat_timeline(alerts)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True, key=f"timeline_{int(time.time())}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        verdict_fig = create_verdict_distribution(alerts)
        if verdict_fig:
            st.plotly_chart(verdict_fig, use_container_width=True, key=f"verdict_{int(time.time())}")

# Auto-refresh
time.sleep(refresh_s)
st.rerun()