"""
StadiumPulse FastAPI Server: External Connectivity Layer.

This module provides a production-grade RESTful interface for external systems
to synchronize sensor data, trigger operational simulations, and audit
the strategic reasoning of the StadiumPulse agentic cluster.
"""

from fastapi import FastAPI, HTTPException, Security, Depends, Body
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel, Field
import json
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add project root and src to path for consistent imports
root_path: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from src.core.models import StadiumState, OptimizerAction
from src.core.venues import NARENDRA_MODI_STADIUM
from src.core.settings import settings
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.simulation.scenario_engine import ScenarioEngine

# --- Security Configuration ---
API_KEY_NAME: str = "X-API-Key"
api_key_header: APIKeyHeader = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
STADIUM_API_KEY: str = settings.STADIUM_API_KEY


from fastapi import Header
from src.services.recaptcha_service import recaptcha_service

async def get_api_key(
    api_key: str = Security(api_key_header),
    recaptcha_token: str = Header(None, alias="X-Recaptcha-Token")
) -> str:
    """
    Validates API key and enforces automated-bot protection via reCAPTCHA v3.
    """
    if api_key != STADIUM_API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate API Key")
        
    if not recaptcha_service.verify_token(recaptcha_token):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="reCAPTCHA verification failed")
        
    return api_key


# --- OpenAPI Models ---


class StateUpdate(BaseModel):
    """Schema for pushing real-time sensor updates to the digital twin."""

    occupancy: Dict[str, int] = Field(..., json_schema_extra={"example": {"S1": 8500}})
    wait_times: Dict[str, float] = Field(..., json_schema_extra={"example": {"G1": 15.5}})


class SimulationRequest(BaseModel):
    """Schema for triggering synthetic operational stress scenarios."""

    scenario_type: str = Field(..., json_schema_extra={"example": "concession_spike"})
    severity: int = Field(default=1, json_schema_extra={"example": 2})


# --- Application Initialization ---

app: FastAPI = FastAPI(
    title="StadiumPulse API",
    description="""
    ## Orchestrating stadium crowds with AI.

    This API allows developers to:
    * **Monitor** real-time occupancy and congestion signals.
    * **Sync** digital twin data with external IoT sensors.
    * **Audit** the strategic reasoning of the Gemini-powered Optimizer Agent.
    * **Simulate** operational stress for training and validation.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Persistence Layer ---
STATE_FILE_PATH: str = "current_stadium_state.json"

# --- Global Agent Cluster (Singletons) ---
pulse_agent: PulseAgent = PulseAgent(STATE_FILE_PATH)
optimizer_agent: OptimizerAgent = OptimizerAgent(NARENDRA_MODI_STADIUM)
simulation_engine: ScenarioEngine = ScenarioEngine(NARENDRA_MODI_STADIUM)

# --- API Endpoints ---


@app.get("/", tags=["System"])
async def read_root() -> Dict[str, str]:
    """System health check and version metadata."""
    return {"status": "online", "system": "StadiumPulse", "version": "1.0.0"}


@app.get("/stadium/state", response_model=Dict[str, Any], tags=["Monitoring"])
async def get_stadium_state(api_key: str = Depends(get_api_key)) -> Dict[str, Any]:
    """
    ### Retrieve Current Venue Metrics
    Returns the real-time occupancy and wait-time distribution across the stadium.
    """
    state_obj: StadiumState = pulse_agent.scan_stadium_state()
    return state_obj.model_dump()


@app.post("/stadium/update", tags=["Integration"])
async def update_stadium_state(
    update: StateUpdate = Body(...), api_key: str = Depends(get_api_key)
) -> Dict[str, str]:
    """
    ### Push External Sensor Data
    Synchronize the digital twin with external crowd-counting sensors or gate control systems.
    """
    try:
        with open(STATE_FILE_PATH, "w") as f:
            json.dump(update.model_dump(), f, indent=2)
        return {"status": "success", "message": "Stadium state synchronized."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}")


@app.get("/optimizer/decision", response_model=OptimizerAction, tags=["AI Reasoning"])
async def get_optimizer_decision(api_key: str = Depends(get_api_key)) -> Dict[str, Any]:
    """
    ### Audit Strategic Play
    Executes the Optimizer Agent's evaluation loop.
    Triggers the **Gemini 1.5 Flash** reasoning engine if congestion > 85%.
    """
    current_state: StadiumState = pulse_agent.scan_stadium_state()
    decision_json: str = optimizer_agent.evaluate_plays(current_state)
    return json.loads(decision_json)


@app.post("/simulation/run", tags=["Simulation"])
async def run_simulation(
    req: SimulationRequest = Body(...), api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    ### Trigger Chaos Scenario
    Artificially injects congestion spikes to test the autonomous response of the agents.
    """
    if req.scenario_type == "nominal":
        state: StadiumState = simulation_engine.generate_nominal_state()
    elif req.scenario_type == "gate_spike":
        state = simulation_engine.inject_congestion_spike(
            simulation_engine.generate_nominal_state(),
            target_type="gate",
            severity_count=req.severity,
        )
    elif req.scenario_type == "concession_spike":
        state = simulation_engine.inject_congestion_spike(
            simulation_engine.generate_nominal_state(),
            target_type="concession",
            severity_count=req.severity,
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported scenario type.")

    with open(STATE_FILE_PATH, "w") as f:
        json.dump(state.model_dump(), f, indent=2)

    return {
        "status": "simulation_triggered",
        "scenario": req.scenario_type,
        "severity": req.severity,
        "timestamp": str(datetime.now()),
    }


if __name__ == "__main__":
    import uvicorn

    # Environment variable port binding for Cloud Run compatibility
    server_port: int = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=server_port)
