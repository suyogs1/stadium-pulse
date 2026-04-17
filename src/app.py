"""
StadiumPulse AI Dashboard: Streamlit Orchestration Console.

Advanced accessibility architecture following logical reading order:
1. Core Controls (Top/Sidebar)
2. Agent Intelligence (Operational Console)
3. Geospatial Mapping (Visual Heatmap)
"""

import streamlit as st
import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root and src to path for consistent imports
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from config import STADIUM_MAP, StadiumState, StadiumConfig, STADIUM_API_KEY, GEMINI_API_KEY
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent
from src.simulation.scenario_engine import ScenarioEngine
from src.services.gemini_reasoner import gemini_ai

# --- Configuration & State Management ---

STATE_FILE_PATH = "current_stadium_state.json"
API_BASE_URL = os.getenv("STADIUM_API_URL", "http://localhost:8080")

if 'venue_id' not in st.session_state: st.session_state.venue_id = "modi"
if 'demo_active' not in st.session_state: st.session_state.demo_active = False
if 'demo_step' not in st.session_state: st.session_state.demo_step = 1
if 'ui_theme' not in st.session_state: st.session_state.ui_theme = "Dark"

PLAYBOOK_PHASES = {
    1: {"name": "Data Ingestion", "desc": "Aggregating historical BQ baselines & IoT telemetry.", "icon": "📥"},
    2: {"name": "System Analysis", "desc": "Calculating venue-wide Load/Capacity distribution.", "icon": "📊"},
    3: {"name": "Bottleneck Detection", "desc": "Pinpointing specific infrastructure pressure points.", "icon": "⚠️"},
    4: {"name": "Strategy Evaluation", "desc": "Engaging Optimizer agent clusters & Gemini Flash AI.", "icon": "🧠"},
    5: {"name": "Action Selection", "desc": "Selecting the optimal intervention play.", "icon": "🎯"},
    6: {"name": "Crowd Redistribution", "desc": "Dispatching alerts & monitoring the resolution loop.", "icon": "🔄"}
}

THEMES = {
    "Dark": {
        "bg_main": "#050505",
        "bg_gradient": "radial-gradient(circle at top right, #0a0a1a, #050505)",
        "text_main": "#ffffff",
        "text_header": "#00d4ff",
        "card_bg": "rgba(30, 30, 40, 0.7)",
        "card_border": "rgba(255, 255, 255, 0.2)",
        "accent": "#00d4ff",
        "status_green": "#00ff64", "status_yellow": "#ffc800", "status_red": "#ff3232"
    },
    "Light": {
        "bg_main": "#ffffff",
        "bg_gradient": "linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)",
        "text_main": "#1a1a1a",
        "text_header": "#0055ff",
        "card_bg": "rgba(255, 255, 255, 0.9)",
        "card_border": "rgba(0, 0, 0, 0.15)",
        "accent": "#0055ff",
        "status_green": "#008f39", "status_yellow": "#b8860b", "status_red": "#cc0000"
    },
    "High Contrast": {
        "bg_main": "#000000", 
        "bg_gradient": "linear-gradient(#000000, #000000)", 
        "text_main": "#ffff00", 
        "text_header": "#ffffff", 
        "card_bg": "#000000", 
        "card_border": "#ffffff",
        "accent": "#ffff00", 
        "status_green": "#00ff00", 
        "status_yellow": "#ffff00", 
        "status_red": "#ff0000"
    }
}

theme = THEMES[st.session_state.ui_theme]

# --- UI Methods ---

def get_stadium_metrics() -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/stadium/state", headers={"X-API-Key": STADIUM_API_KEY}, timeout=0.8)
        if response.status_code == 200: return response.json()
    except Exception: pass
    if not os.path.exists(STATE_FILE_PATH): return {"occupancy": {}, "wait_times": {}}
    with open(STATE_FILE_PATH, 'r') as f: return json.load(f)

def get_orchestration_decision(current_pulse: StadiumState) -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/optimizer/decision", headers={"X-API-Key": STADIUM_API_KEY}, timeout=2.5)
        if response.status_code == 200: return response.json()
    except Exception: pass
    opt = OptimizerAgent(STADIUM_MAP[st.session_state.venue_id])
    return json.loads(opt.evaluate_plays(current_pulse))

def persist_stadium_state_local(state_data: Dict[str, Any]) -> None:
    with open(STATE_FILE_PATH, 'w') as f: json.dump(state_data, f, indent=2)

# --- THEME INJECTION ---

st.set_page_config(page_title="StadiumPulse AI Console", layout="wide", page_icon="📡")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {{ 
        font-family: 'Outfit', sans-serif; 
        background-color: {theme['bg_main']} !important; 
        color: {theme['text_main']} !important; 
    }}
    
    .stApp {{ 
        background: {theme['bg_gradient']} !important; 
    }}
    
    .glass-card {{ 
        background: {theme['card_bg']}; 
        border: 2px solid {theme['card_border']}; 
        border-radius: 12px; 
        padding: 1.25rem; 
        height: 100%; 
        backdrop-filter: blur(10px); 
        margin-bottom: 20px; 
        color: {theme['text_main']} !important;
    }}
    
    .agent-title {{ 
        font-size: 0.9rem; 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        color: {theme['accent']} !important; 
        margin-bottom: 1rem; 
        font-weight: 700; 
        display: flex; 
        align-items: center; 
        gap: 8px; 
    }}
    
    .reasoning-line {{ 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 0.8rem; 
        color: {theme['text_main']} !important; 
        opacity: 0.8; 
        margin-bottom: 6px; 
        border-left: 2px solid {theme['accent']}; 
        padding-left: 10px; 
    }}
    
    .ai-label {{ 
        font-size: 0.75rem; 
        font-weight: 700; 
        color: #ff55ff; 
        background: rgba(255, 85, 255, 0.1); 
        padding: 2px 8px; 
        border-radius: 4px; 
        display: inline-block; 
        margin-bottom: 8px; 
    }}
    
    .ai-step {{ 
        font-size: 0.8rem; 
        margin-bottom: 5px; 
        color: {theme['text_main']} !important;
    }}
    
    .ai-step b {{ 
        color: {theme['accent']} !important; 
    }}
    
    .stat-val {{ 
        font-size: 1.5rem; 
        font-weight: 700; 
        color: {theme['text_header']} !important; 
    }}
    
    .stat-label {{ 
        font-size: 0.75rem; 
        color: {theme['text_main']} !important; 
        opacity: 0.7; 
        text-transform: uppercase; 
        font-weight: 600; 
    }}
    
    .status-pill {{ 
        padding: 3px 10px; 
        border-radius: 15px; 
        font-size: 0.7rem; 
        font-weight: 800; 
        display: inline-block; 
        border: 2px solid transparent; 
    }}
    
    .status-green {{ color: {theme['status_green']} !important; border-color: {theme['status_green']} !important; }}
    .status-yellow {{ color: {theme['status_yellow']} !important; border-color: {theme['status_yellow']} !important; }}
    .status-red {{ color: {theme['status_red']} !important; border-color: {theme['status_red']} !important; }}
    
    h1, h2, h3, h4, h5 {{ color: {theme['text_header']} !important; margin-bottom: 0.5rem !important; }}
    p, span, div, label {{ color: {theme['text_main']} !important; }}
    
    /* Streamlit widget overrides */
    .stSelectbox label, .stButton button {{ color: {theme['text_main']} !important; }}
    .stMarkdown p {{ color: {theme['text_main']} !important; }}
</style>
""", unsafe_allow_html=True)

# --- TOP SECTION ---

top_col1, top_col2, top_col3 = st.columns([3, 1, 1])
with top_col1:
    st.title("📡 StadiumPulse")
    st.markdown("##### Agentic Crowd Orchestration Platform")
with top_col2:
    st.session_state.venue_id = st.selectbox(
        "Active Venue Select", 
        options=["modi", "wankhede", "wembley"], 
        format_func=lambda x: STADIUM_MAP[x].stadium_name,
        help="Select the physical stadium venue for real-time monitoring."
    )
with top_col3:
    st.session_state.ui_theme = st.selectbox(
        "Appearance Theme", 
        options=["Dark", "Light", "High Contrast"],
        help="Adjust the UI aesthetic for optimal readability and accessibility."
    )

st.write("---")

st.header("1. Operational Pulse Console")
st.caption("Real-time telemetry and AI strategic reasoning from the agentic cluster.")

# --- ROW 1: THREE PANELS ---

metrics = get_stadium_metrics()
pulse_obj = StadiumState(**metrics)
decision_payload = get_orchestration_decision(pulse_obj)

col_pulse, col_optimizer, col_messenger = st.columns(3, gap="medium")

with col_pulse:
    st.markdown(f'<div class="glass-card"><div class="agent-title">🔍 Pulse Agent</div>', unsafe_allow_html=True)
    load_sum = sum(metrics['occupancy'].values())
    avg_load = load_sum / len(STADIUM_MAP[st.session_state.venue_id].sections) if STADIUM_MAP[st.session_state.venue_id].sections else 0
    m1, m2 = st.columns(2)
    m1.markdown(f'<div class="stat-label">Avg Load</div><div class="stat-val">{avg_load:,.0f}</div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="stat-label">Active Alerts</div><div class="stat-val">{len([w for w in metrics["wait_times"].values() if w > 15])}</div>', unsafe_allow_html=True)
    st.write("Recent Activity:")
    for section in STADIUM_MAP[st.session_state.venue_id].sections[:3]:
        pop = metrics['occupancy'].get(section.section_id, 0)
        util = (pop / section.capacity) * 100
        pill = "status-green"
        if util > 90: pill = "status-red"
        elif util > 70: pill = "status-yellow"
        st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.8rem;"><span>{section.section_id}</span><span class="status-pill {pill}">{util:.0f}%</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_optimizer:
    st.markdown(f'<div class="glass-card"><div class="agent-title">🧠 Optimizer Brain</div>', unsafe_allow_html=True)
    
    if decision_payload.get('is_ai_decision'):
        st.markdown('<div class="ai-label">Gemini Strategic Analysis</div>', unsafe_allow_html=True)
        meta = decision_payload.get('ai_metadata', {})
        st.markdown(f'<div class="ai-step"><b>Observation:</b> {meta.get("observation")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-step"><b>Analysis:</b> {meta.get("analysis")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-step"><b>Decision:</b> {meta.get("decision")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-step"><b>Strategy:</b> {meta.get("strategy")}</div>', unsafe_allow_html=True)
        st.caption(f"Reasoning ID: {decision_payload.get('reasoning_id')} | {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.markdown(f"**Action:** `{decision_payload['action_type']}`")
        for log_step in decision_payload['reasoning_trace'][-3:]:
            st.markdown(f'<div class="reasoning-line">{log_step}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="stat-label" style="margin-top:10px;">Budget</div><div class="stat-val">{decision_payload["budget_remaining"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_messenger:
    st.markdown(f'<div class="glass-card"><div class="agent-title">📢 Messenger Dispatch</div>', unsafe_allow_html=True)
    if decision_payload['action_type'] != "MONITOR_ONLY":
        msg = "Distributing incentives..." if "INCENTIVIZE" in decision_payload['action_type'] else "Redirecting ingress..."
        st.info(msg)
        st.markdown(f"**Target:** `{', '.join(decision_payload['target_entities'][:2])}...`")
    else:
        st.success("All systems nominal.")
    if not gemini_ai.api_active: st.warning("Simulation Mode Active")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 2: PLAYBOOK ---

st.subheader("🛠️ Operational Playbook Timeline")
active_playbook = st.container()
with active_playbook:
    p_cols = st.columns(6)
    for i, (step_id, info) in enumerate(PLAYBOOK_PHASES.items()):
        is_active = st.session_state.demo_step == step_id
        opacity = "1" if is_active else "0.3"
        border = f"2px solid {theme['accent']}" if is_active else "1px solid #333"
        p_cols[i].markdown(f"""
        <div style="opacity:{opacity}; border:{border}; padding:10px; border-radius:8px; text-align:center; height:90px;">
            <div style="font-size:1.2rem;">{info['icon']}</div>
            <div style="font-size:0.7rem; font-weight:700;">{info['name']}</div>
        </div>
        """, unsafe_allow_html=True)

pb_col1, pb_col2, pb_col3 = st.columns([1, 4, 1])
if pb_col1.button("⏮️ Prev", use_container_width=True) and st.session_state.demo_step > 1:
    st.session_state.demo_step -= 1
    st.rerun()
pb_col2.markdown(f'<div style="text-align:center; font-weight:700; color:{theme["accent"]};">{PLAYBOOK_PHASES[st.session_state.demo_step]["desc"]}</div>', unsafe_allow_html=True)
if pb_col3.button("Next ⏭️", use_container_width=True) and st.session_state.demo_step < 6:
    st.session_state.demo_step += 1
    st.rerun()

# --- ROW 3: HEATMAP ---

st.write("---")
st.subheader("Geospatial Congestion Mapping")
venue_config = STADIUM_MAP[st.session_state.venue_id]
svg_nodes = []
for section in venue_config.sections:
    current_pop = metrics['occupancy'].get(section.section_id, 0)
    ratio = current_pop / section.capacity
    color = theme["status_red"] if ratio > 0.9 else theme["status_yellow"] if ratio > 0.7 else theme["status_green"]
    x, y = section.x, section.y
    svg_nodes.append(f'<circle cx="{x}" cy="{y}" r="35" fill="{color}" stroke="{theme["card_border"]}" stroke-width="2" aria-label="Section {section.section_id}"/><text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="middle" fill="{theme["bg_main"]}" font-weight="bold" font-size="12">{section.section_id}</text>')

stadium_svg = f'<div style="display:flex; justify-content:center; padding:20px; border-radius:12px;" role="img" aria-label="Stadium Heatmap"><svg width="400" height="400" viewBox="0 0 400 400">{" ".join(svg_nodes)}</svg></div>'
import streamlit.components.v1 as components
components.html(stadium_svg, height=380)
st.markdown(f'<div style="text-align:center; font-size:0.8rem;"><span style="color:{theme["status_green"]}">● Healthy</span> &nbsp; <span style="color:{theme["status_yellow"]}">● Warning</span> &nbsp; <span style="color:{theme["status_red"]}">● Danger</span></div>', unsafe_allow_html=True)
st.caption("Figure 1: Stadium Pulse Heatmap. Visual status of all sections.")

# --- BOTTOM SECTION: INTEGRATION ---

st.write("---")
with st.expander("🔌 External Integration Portal", expanded=False):
    st.markdown("##### Headless Agentic Orchestration via REST API")
    st.caption(f"Endpoint Base: {API_BASE_URL}")
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        st.markdown("**Telemetry Endpoints**")
        st.code(f'# Fetch Stadium State\ncurl -X GET "{API_BASE_URL}/stadium/state" \\\n  -H "X-API-Key: {STADIUM_API_KEY}"')
        st.code(f'# Fetch Strategic Decisions\ncurl -X GET "{API_BASE_URL}/optimizer/decision" \\\n  -H "X-API-Key: {STADIUM_API_KEY}"')
    with e_col2:
        st.markdown("**Agent Control Endpoints**")
        st.code(f'# Update Infrastructure\ncurl -X POST "{API_BASE_URL}/stadium/update" \\\n  -H "X-API-Key: {STADIUM_API_KEY}" \\\n  -H "Content-Type: application/json" \\\n  -d \'{{"occupancy": {{"S1": 9000}}}}\'')
        st.code(f'# Trigger Agentic Simulation\ncurl -X POST "{API_BASE_URL}/simulation/run" \\\n  -H "X-API-Key: {STADIUM_API_KEY}"')

# Local logic sync
engine = ScenarioEngine(venue_config)
state = engine.generate_nominal_state()
if st.session_state.demo_active or True:
    if st.session_state.demo_step >= 3:
        for s in venue_config.sections: state.occupancy[s.section_id] = int(s.capacity * (0.88 if st.session_state.demo_step < 6 else 0.55))
    persist_stadium_state_local(state.model_dump())

time.sleep(10)
st.rerun()
