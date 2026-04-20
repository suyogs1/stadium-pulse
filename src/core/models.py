"""
Core Domain Models: The StadiumPulse Source of Truth.

Defines the fundamental data structures used throughout the agentic loop,
ensuring a strict typed contract between scanning, analysis, and action.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Section(BaseModel):
    """Represents a discrete seating section within a stadium venue."""

    section_id: str = Field(..., description="Unique identifier for the section (e.g., 'S1')")
    name: str = Field(..., description="Display name of the section")
    capacity: int = Field(..., description="Maximum seating capacity of this sector")
    x: float = Field(0.0, description="X coordinate for spatial mapping")
    y: float = Field(0.0, description="Y coordinate for spatial mapping")
    adjacency_matrix: Dict[str, float] = Field(..., description="Distance to neighbors")


class Gate(BaseModel):
    """Represents an entry/exit portal."""

    gate_id: str = Field(..., description="Unique identifier for the gate")
    name: str = Field(..., description="Display name of the entry portal")


class ConcessionBlock(BaseModel):
    """Represents a food, beverage, or retail facility."""

    block_id: str = Field(..., description="Unique identifier for the concession")
    name: str = Field(..., description="Official name of the concession stand")
    category: str = Field(..., description="Service category")


class StadiumConfig(BaseModel):
    """Complete static physical layout of a venue."""

    model_config = ConfigDict(title="Stadium Configuration Schema")
    stadium_name: str
    sections: List[Section]
    gates: List[Gate]
    concession_blocks: List[ConcessionBlock]


class StadiumState(BaseModel):
    """Real-time telemetry pulse of the entire venue."""

    occupancy: Dict[str, int] = Field(default_factory=dict)
    wait_times: Dict[str, float] = Field(default_factory=dict)


class OptimizerAction(BaseModel):
    """Strategic decision output from the agentic analysis."""

    action_type: str  # MONITOR_ONLY, REROUTE, INCENTIVIZE, PREDICTIVE_BUFFER
    target_entities: List[str]
    reasoning_trace: List[str]
    budget_remaining: int
    is_ai_decision: bool = False
    reasoning_id: Optional[str] = None
    ai_metadata: Optional[Dict[str, str]] = None
