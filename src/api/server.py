"""
StadiumPulse FastAPI Server: External Connectivity Layer.

This module provides a RESTful interface for external systems 
to query stadium state, trigger simulations, and retrieve AI decisions.
"""

from fastapi import FastAPI, HTTPException, Security, Depends, Body
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel, Field
import json
import os
import sys
from typing import Dict, List, Any, Optional

# Ensure project root is in path for relative imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from config import NARENDRA_MODI_STADIUM, StadiumState
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.simulation.scenario_engine import ScenarioEngine

# --- Security Configuration ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
STADIUM_API_KEY = os.getenv("STADIUM_API_KEY", "pulse-secret-default")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validates the incoming API key against the environment variable."""
    if api_key_header == STADIUM_API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API Key"
    )

# --- OpenAPI Models ---

class StateUpdate(BaseModel):
    """Schema for pushing real-time sensor updates."""
    occupancy: Dict[str, int] = Field(
        ..., 
        example={"S1": 8500, "S2": 12000},
        description="Map of section IDs to headcounts."
    )
    wait_times: Dict[str, float] = Field(
        ..., 
        example={"G1": 15.5, "C1": 8.0},
        description="Map of gate or concession IDs to wait times in minutes."
    )

class SimulationRequest(BaseModel):
    """Schema for triggering synthetic operational scenarios."""
    scenario_type: str = Field(
        ..., 
        example="concession_spike",
        description="Type of emergency: nominal, gate_spike, concession_spike."
    )
    severity: int = Field(
        default=1, 
        example=2,
        description="Number of infrastructure nodes to affect."
    )

class OptimizerDecisionResponse(BaseModel):
    """Schema for the AI's strategic output."""
    action_type: str = Field(..., example="INCENTIVIZE")
    target_entities: List[str] = Field(..., example=["C1", "C2"])
    reasoning_trace: List[str] = Field(..., example=["Phase 1: Scan", "Phase 2: Detect Surge"])
    budget_remaining: int = Field(..., example=80)
    timestamp: str = Field(..., example="2026-04-16T12:00:00")
    is_ai_decision: bool = Field(default=False)
    reasoning_id: Optional[str] = Field(default=None)
    ai_metadata: Optional[Dict[str, str]] = Field(default=None)

# --- Application Initialization ---

app = FastAPI(
    title="StadiumPulse API",
    description="""
    ## Orchestrating stadium crowds with AI.
    
    This API allows developers to:
    * **Monitor** real-time occupancy and congestion signals.
    * **Inject** sensor data from third-party vendor systems.
    * **Audit** the strategic reasoning of the Gemini-powered Optimizer Agent.
    * **Simulate** stress scenarios for operational training.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Persistent State Path ---
STATE_FILE_PATH = "current_stadium_state.json"

# --- Agent Initialization ---
pulse_agent = PulseAgent(STATE_FILE_PATH)
optimizer_agent = OptimizerAgent(NARENDRA_MODI_STADIUM)
simulation_engine = ScenarioEngine(NARENDRA_MODI_STADIUM)

# --- API Endpoints ---

@app.get("/", tags=["System"])
async def root():
    """System health check and version metadata."""
    return {"status": "online", "system": "StadiumPulse", "version": "1.0.0"}

@app.get("/stadium/state", response_model=Dict[str, Any], tags=["Monitoring"])
async def get_stadium_state(api_key: str = Depends(get_api_key)):
    """
    ### Retrieve Current Venue Metrics
    Returns the real-time occupancy and wait-time distribution across the stadium infrastructure.
    """
    state = pulse_agent.scan_stadium_state()
    return state.model_dump()

@app.post("/stadium/update", tags=["Integration"])
async def update_stadium_state(
    update: StateUpdate = Body(...), 
    api_key: str = Depends(get_api_key)
):
    """
    ### Push External Sensor Data
    Synchronize the digital twin with external crowd-counting sensors or gate control systems.
    """
    try:
        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(update.model_dump(), f, indent=2)
        return {"status": "success", "message": "Stadium state synchronized."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/optimizer/decision", response_model=OptimizerDecisionResponse, tags=["AI Reasoning"])
async def get_optimizer_decision(api_key: str = Depends(get_api_key)):
    """
    ### Audit Strategic Play
    Executes the Optimizer Agent's evaluation loop. If load is >85%, this triggers the **Gemini 1.5 Flash** reasoning engine.
    """
    current_state = pulse_agent.scan_stadium_state()
    decision_json = optimizer_agent.evaluate_plays(current_state)
    return json.loads(decision_json)

@app.post("/simulation/run", tags=["Simulation"])
async def run_simulation(
    req: SimulationRequest = Body(...), 
    api_key: str = Depends(get_api_key)
):
    """
    ### Trigger Chaos Scenario
    Artificially injects congestion spikes into the venue to test the autonomous response of the orchestration agents.
    """
    if req.scenario_type == "nominal":
        state = simulation_engine.generate_nominal_state()
    elif req.scenario_type == "gate_spike":
        state = simulation_engine.inject_congestion_spike(
            simulation_engine.generate_nominal_state(), 
            target_type="gate", 
            severity_count=req.severity
        )
    elif req.scenario_type == "concession_spike":
        state = simulation_engine.inject_congestion_spike(
            simulation_engine.generate_nominal_state(), 
            target_type="concession", 
            severity_count=req.severity
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported scenario type.")

    with open(STATE_FILE_PATH, 'w') as f:
        json.dump(state.model_dump(), f, indent=2)

    return {"status": "simulation_triggered", "scenario": req.scenario_type, "severity": req.severity}

if __name__ == "__main__":
    import uvicorn
    if "--dev" in sys.argv:
        from scripts.run_tests import run_tests
        if not run_tests():
            print("\nCRITICAL: API Server pre-flight check failed. Aborting startup.")
            sys.exit(1)

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
