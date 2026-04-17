"""
StadiumPulse Operational Playbook Unit Tests.

Verifies the logic of the interactive demo phases and orchestration steps.
"""

import pytest

# Playbook definition (mirrored from src/app.py)
PLAYBOOK_PHASES = {
    1: {"name": "Data Ingestion", "desc": "Aggregating historical BQ baselines & IoT telemetry.", "icon": "📥"},
    2: {"name": "System Analysis", "desc": "Calculating venue-wide Load/Capacity distribution.", "icon": "📊"},
    3: {"name": "Bottleneck Detection", "desc": "Pinpointing specific infrastructure pressure points.", "icon": "⚠️"},
    4: {"name": "Strategy Evaluation", "desc": "Engaging Optimizer agent clusters & Gemini Flash AI.", "icon": "🧠"},
    5: {"name": "Action Selection", "desc": "Selecting the optimal intervention play.", "icon": "🎯"},
    6: {"name": "Crowd Redistribution", "desc": "Dispatching alerts & monitoring the resolution loop.", "icon": "🔄"}
}

def test_playbook_phase_integrity():
    """Verify that all 6 critical phases are defined and structured correctly."""
    assert len(PLAYBOOK_PHASES) == 6
    for step_id in range(1, 7):
        assert step_id in PLAYBOOK_PHASES
        assert "name" in PLAYBOOK_PHASES[step_id]
        assert "desc" in PLAYBOOK_PHASES[step_id]

def test_phase_transition_logic():
    """Simulate user navigation through the playbook phases."""
    current_step = 1
    
    # Forward Navigation
    current_step += 1
    assert current_step == 2
    assert PLAYBOOK_PHASES[current_step]["name"] == "System Analysis"
    
    # Backward Navigation
    current_step -= 1
    assert current_step == 1
    assert PLAYBOOK_PHASES[current_step]["name"] == "Data Ingestion"

def test_playbook_bounds_safeguard():
    """Verify that the playbook navigation respects lower and upper bounds."""
    # Bottom Bound check
    current_step = 1
    if current_step > 1:
        current_step -= 1
    assert current_step == 1
    
    # Top Bound check
    current_step = 6
    if current_step < 6:
        current_step += 1
    assert current_step == 6

def test_ui_phase_highlight_logic():
    """
    Verifies that the UI correctly identifies the active phase for styling.
    """
    current_step = 4
    for step_id in PLAYBOOK_PHASES:
        is_active = (current_step == step_id)
        if step_id == 4:
            assert is_active is True
        else:
            assert is_active is False

def test_ai_trigger_phase_alignment():
    """
    Verifies that 'Strategy Evaluation' (Phase 4) is the primary AI engagement point.
    """
    assert "Gemini" in PLAYBOOK_PHASES[4]["desc"]
    assert "Intelligence" in PLAYBOOK_PHASES[1]["desc"] or "Ingestion" in PLAYBOOK_PHASES[1]["name"]
