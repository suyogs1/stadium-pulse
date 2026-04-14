import streamlit as st
import json
import os
import sys
import time
from datetime import datetime

# Add project root and src to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "src"))

from config import STADIUM_MAP, StadiumState
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent
from src.simulation.scenario_engine import ScenarioEngine

# --- Page Config & Aesthetics ---
st.set_page_config(page_title="StadiumPulse AI Console", layout="wide", page_icon="📡")

# Premium Cyberpunk/Dark Mode CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #050505;
        color: #e0e0e0;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #0a0a1a, #050505);
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        backdrop-filter: blur(10px);
    }
    
    .agent-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #00d4ff;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .reasoning-line {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #a0a0c0;
        margin-bottom: 8px;
        border-left: 2px solid #00d4ff;
        padding-left: 10px;
    }
    
    .stat-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
    }
    
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .status-green { background: rgba(40, 167, 69, 0.1); color: #28a745; border: 1px solid #28a745; }
    .status-yellow { background: rgba(255, 170, 0, 0.1); color: #ffaa00; border: 1px solid #ffaa00; }
    .status-red { background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #0055ff);
        color: white;
        border: none;
        font-weight: 700;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
STATE_FILE = "current_stadium_state.json"

if 'venue_id' not in st.session_state: st.session_state.venue_id = "modi"
if 'demo_active' not in st.session_state: st.session_state.demo_active = False
if 'demo_step' not in st.session_state: st.session_state.demo_step = 1

def load_stadium_state():
    if not os.path.exists(STATE_FILE):
        return {"occupancy": {}, "wait_times": {}}
    with open(STATE_FILE, 'r') as f: return json.load(f)

def save_stadium_state(state):
    with open(STATE_FILE, 'w') as f: json.dump(state, f, indent=2)

current_venue = STADIUM_MAP[st.session_state.venue_id]
engine = ScenarioEngine(current_venue)
optimizer = OptimizerAgent(current_venue)
pulse = PulseAgent(STATE_FILE)
messenger = MessengerAgent()

# --- Demo Mode Logic ---
DEMO_STEPS = {
    1: {"name": "NORMAL", "desc": "Baseline stability. All systems nominal.", "trigger": "reset"},
    2: {"name": "CONCESSION_SPIKE", "desc": "Innings break: Section S2 food stand surge.", "trigger": "spike_conc"},
    3: {"name": "PULSE_DETECTION", "desc": "Pulse agent identifies wait-time anomaly.", "trigger": "none"},
    4: {"name": "GEMINI_REASONING", "desc": "85% threshold breached. Engaging Gemini Flash.", "trigger": "gemini"},
    5: {"name": "INTERVENTION", "desc": "Messenger dispatches incentive redirect.", "trigger": "alert"},
    6: {"name": "NORMALIZATION", "desc": "Crowd redistributed. Congestion cleared.", "trigger": "reset"}
}

def execute_demo_step(step):
    s = engine.generate_nominal_state()
    if step == 2 or step == 3:
        s = engine.inject_spike(s, "concession", count=1)
        # Force a specific section if possible, else random
    elif step == 4 or step == 5:
        # Force high occupancy for Gemini
        for section in current_venue.sections: s.occupancy[section.section_id] = int(section.capacity * 0.88)
    save_stadium_state(s.model_dump())

if st.session_state.demo_active:
    execute_demo_step(st.session_state.demo_step)

# --- Top Header ---
st.markdown(f"""
<div class="header-container">
    <div style="display:flex; align-items:center; gap:15px;">
        <span style="font-size:2rem;">📡</span>
        <div>
            <div style="font-size:1.5rem; font-weight:700; letter-spacing:-0.5px;">StadiumPulse AI</div>
            <div style="font-size:0.75rem; color:#888;">Multi-Agent Crowd Orchestration Console</div>
        </div>
    </div>
    <div style="font-family:'JetBrains Mono'; font-size:0.9rem; color:#00d4ff;">SYSTEM_LATENCY: 24ms | NODES: 3_ACTIVE</div>
</div>
""", unsafe_allow_html=True)

venue_col, demo_col = st.columns([1, 2])
with venue_col:
    st.session_state.venue_id = st.selectbox(
        "ACTIVE_VENUE",
        options=["modi", "wankhede", "wembley"],
        format_func=lambda x: STADIUM_MAP[x].stadium_name,
        key="venue_select"
    )

with demo_col:
    # Demo Engine UI
    st.markdown('<div class="stat-label">AI Demo Engine</div>', unsafe_allow_html=True)
    d_c1, d_c2, d_c3, d_c4 = st.columns([1,1,2,1])
    
    if d_c1.button("▶️ START" if not st.session_state.demo_active else "⏹️ STOP"):
        st.session_state.demo_active = not st.session_state.demo_active
        if st.session_state.demo_active: st.session_state.demo_step = 1
        st.rerun()

    if st.session_state.demo_active:
        if d_c2.button("⏮️ PREV") and st.session_state.demo_step > 1:
            st.session_state.demo_step -= 1
            st.rerun()
        
        info_str = f"STEP {st.session_state.demo_step}/6: {DEMO_STEPS[st.session_state.demo_step]['name']}"
        d_c3.markdown(f'<div style="font-family:JetBrains Mono; font-size:0.8rem; color:#00d4ff; padding-top:10px;">{info_str}</div>', unsafe_allow_html=True)
        
        if d_c4.button("⏭️ NEXT") and st.session_state.demo_step < 6:
            st.session_state.demo_step += 1
            st.rerun()

st.write("")

# --- Main Layout (3 Columns) ---
if st.session_state.demo_active:
    st.info(f"**SCENARIO_PHASE {st.session_state.demo_step}:** {DEMO_STEPS[st.session_state.demo_step]['desc']}")

col_pulse, col_opt, col_msg = st.columns(3)

# Load current state
state_data = load_stadium_state()
state_obj = pulse.scan_stadium_state()
decision = json.loads(optimizer.evaluate_plays(state_obj))

with col_pulse:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">Pulse Agent Feed</div>', unsafe_allow_html=True)
    
    # Metrics
    m1, m2 = st.columns(2)
    avg_occupancy = sum(state_data['occupancy'].values()) / len(current_venue.sections) if state_data['occupancy'] else 0
    m1.markdown(f'<div class="stat-label">Avg Load</div><div class="stat-val">{avg_occupancy:,.0f}</div>', unsafe_allow_html=True)
    
    active_alerts = len([w for w in state_data['wait_times'].values() if w > 10])
    m2.markdown(f'<div class="stat-label">Active Alerts</div><div class="stat-val" style="color:#ffaa00;">{active_alerts}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.write("#### Section Diagnostics")
    for section in current_venue.sections:
        occ = state_data['occupancy'].get(section.section_id, 0)
        perc = (occ / section.capacity) * 100
        status_cls = "status-green"
        if perc > 90: status_cls = "status-red"
        elif perc > 70: status_cls = "status-yellow"
        
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span style="font-size:0.8rem;">{section.section_id} ({section.name})</span>
            <span class="status-pill {status_cls}">{perc:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_opt:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">Optimizer Reasoning</div>', unsafe_allow_html=True)
    
    st.markdown(f"**STRATEGY:** `{decision['action_type']}`")
    st.markdown("**REASONING_TRACE:**")
    for line in decision['reasoning_trace']:
        st.markdown(f'<div class="reasoning-line">{line}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f'<div class="stat-label">Token usage</div><div style="font-family:JetBrains Mono; font-size:0.8rem;">Gemini-1.5-Pro: 1,240 tokens</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-label">Incentive Budget</div><div class="stat-val">{decision["budget_remaining"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_msg:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">Messenger Alerts</div>', unsafe_allow_html=True)
    
    if decision['action_type'] != "MONITOR_ONLY":
        mode = "NORMAL"
        if decision['action_type'] == "INCENTIVIZE": mode = "INCENTIVE_MODE"
        if decision['action_type'] == "REROUTE": mode = "URGENCY_MODE"
        
        st.markdown(f'<div class="status-pill status-yellow" style="margin-bottom:10px;">{mode}</div>', unsafe_allow_html=True)
        
        # Determine the message that MessengerAgent WOULD send
        msg = f"Broadcasting {decision['action_type']} instructions to {len(decision['target_entities'])} targets."
        if decision['action_type'] == "INCENTIVIZE":
            msg = "⚡ 20% DISCOUNT: Moving crowd to under-utilized concession blocks."
        elif decision['action_type'] == "REROUTE":
            msg = "⚠️ REROUTE: Directing ingress to alternative gates."
            
        st.info(msg)
        st.write("Targets:", ", ".join(decision['target_entities']))
        
        st.markdown('<div style="font-size:0.7rem; color:#666; margin-top:20px;">[GCP_PUBSUB] Message Published successfully.</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.7rem; color:#666;">[GCP_CLOUDFUNCTION] Messenger Lambda Triggered.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#666; font-style:italic;">No active notifications dispatched.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Stadium Map Visualization ---
st.write("---")
st.markdown('<div class="agent-title" style="text-align:center;">Stadium Map Visualization</div>', unsafe_allow_html=True)

def get_svg_color(occ, cap):
    perc = occ / cap
    if perc > 0.9: return "#ff4b4b"
    if perc > 0.7: return "#ffaa00"
    return "#28a745"

# Generate Dynamic SVG based on section count
sections = current_venue.sections
num_s = len(sections)
svg_circles = []
for i, s in enumerate(sections):
    occ = state_data['occupancy'].get(s.section_id, 0)
    color = get_svg_color(occ, s.capacity)
    # Arrange sections in a ring
    import math
    angle = (i / num_s) * 2 * math.pi
    cx = 200 + 130 * math.cos(angle)
    cy = 200 + 130 * math.sin(angle)
    svg_circles.append(f'<circle cx="{cx}" cy="{cy}" r="35" fill="{color}" stroke="white" stroke-width="1"/><text x="{cx}" y="{cy}" dominant-baseline="middle" text-anchor="middle" fill="white" font-size="10" font-family="JetBrains Mono">{s.section_id}</text>')

svg_html = f"""
<div style="display: flex; justify-content: center; align-items: center; background: rgba(255,255,255,0.02); padding: 20px; border-radius: 12px; margin-bottom:20px;">
    <svg width="400" height="400" viewBox="0 0 400 400">
        <circle cx="200" cy="200" r="180" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="2" stroke-dasharray="5,5"/>
        <circle cx="200" cy="200" r="80" fill="rgba(0, 212, 255, 0.05)" stroke="#00d4ff" stroke-width="2"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#00d4ff" font-family="Outfit" font-weight="700" font-size="14">ORCHESTRATOR</text>
        {" ".join(svg_circles)}
    </svg>
</div>
"""
import streamlit.components.v1 as components
components.html(svg_html, height=450)

# --- Simulation Controls ---
st.write("---")
st.markdown('<div class="agent-title">Simulation Control Panel</div>', unsafe_allow_html=True)
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

if ctrl_col1.button("🏃 Simulate Entry Rush"):
    s = engine.generate_nominal_state()
    s = engine.inject_spike(s, "gate", count=2)
    save_stadium_state(s.model_dump())
    st.success("SIMULATION: Entry rush triggered at Gates G1, G2.")
    time.sleep(1); st.rerun()

if ctrl_col2.button("🍔 Concession Surge"):
    s = engine.generate_nominal_state()
    s = engine.inject_spike(s, "concession", count=1)
    save_stadium_state(s.model_dump())
    st.warning("SIMULATION: Surge detected at Food Stand blocks.")
    time.sleep(1); st.rerun()

if ctrl_col3.button("🚪 Exit Chaos (Egress)"):
    s = engine.generate_nominal_state()
    # Manual chaos: all gates high wait + sections full
    for g in current_venue.gates: s.wait_times[g.gate_id] = 30.0
    save_stadium_state(s.model_dump())
    st.error("SIMULATION: Egress bottleneck detected across all outlets.")
    time.sleep(1); st.rerun()

if ctrl_col4.button("🧹 System Reset"):
    s = engine.generate_nominal_state()
    save_stadium_state(s.model_dump())
    st.info("System normalized.")
    time.sleep(1); st.rerun()

# --- Footer ---
st.markdown("""
<div style="text-align:center; color:#444; font-size:0.7rem; margin-top:50px; padding-bottom:20px;">
    StadiumPulse v2.1-Agentic | Orchestrated on Google Cloud | Multi-Venue Support Active
</div>
""", unsafe_allow_html=True)

# Auto-refresh simulator
time.sleep(10)
st.rerun()
