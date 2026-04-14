"""
Configuration and State Models for StadiumPulse.
This module defines the schema and real-time state models for stadium management,
specifically tailored for 'Narendra Modi Stadium'.
"""

from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict


class Section(BaseModel):
    """Represents a seating section in the stadium."""
    section_id: str = Field(..., description="Unique identifier for the section")
    name: str = Field(..., description="Display name of the section")
    capacity: int = Field(..., description="Maximum seating capacity")
    adjacency_matrix: Dict[str, float] = Field(
        ...,
        description="Distance in meters to other sections (section_id -> distance)"
    )


class Gate(BaseModel):
    """Represents an entry/exit gate."""
    gate_id: str = Field(..., description="Unique identifier for the gate")
    name: str = Field(..., description="Display name of the gate")


class ConcessionBlock(BaseModel):
    """Represents a food or drink concession stand."""
    block_id: str = Field(..., description="Unique identifier for the concession block")
    name: str = Field(..., description="Display name of the concession")
    category: str = Field(..., description="Type of concession (e.g., Snacks, Beverages)")


class StadiumConfig(BaseModel):
    """Full static configuration for a stadium."""
    model_config = ConfigDict(title="Stadium Configuration Schema")

    stadium_name: str
    sections: List[Section]
    gates: List[Gate]
    concession_blocks: List[ConcessionBlock]


class StadiumState(BaseModel):
    """Real-time tracking of stadium metrics."""
    # Maps section_id to current occupancy count
    occupancy: Dict[str, int] = Field(
        default_factory=dict,
        description="Real-time occupancy per section"
    )
    # Maps gate_id or block_id to current wait time in minutes
    wait_times: Dict[str, float] = Field(
        default_factory=dict,
        description="Real-time wait times in minutes"
    )


# --- Stadium Configurations ---

def create_stadium_config(name: str, section_count: int, gate_count: int, concession_count: int) -> StadiumConfig:
    """Utility to generate realistic configurations for various venues."""
    sections = []
    for i in range(1, section_count + 1):
        s_id = f"S{i}"
        # Simplified adjacency: neighbors are +1/-1
        adj = {f"S{j}": abs(i - j) * 20.0 for j in range(1, section_count + 1) if i != j}
        sections.append(Section(
            section_id=s_id,
            name=f"{name} Section {i}",
            capacity=int(100000 / section_count), # rough avg
            adjacency_matrix=adj
        ))

    gates = [Gate(gate_id=f"G{i}", name=f"Gate {i}") for i in range(1, gate_count + 1)]
    concessions = [ConcessionBlock(block_id=f"C{i}", name=f"Food Stand {i}", category="Global") for i in range(1, concession_count + 1)]

    return StadiumConfig(
        stadium_name=name,
        sections=sections,
        gates=gates,
        concession_blocks=concessions
    )

# Pre-defined Venues
NARENDRA_MODI_STADIUM = create_stadium_config("Narendra Modi Stadium", 10, 4, 6)
WANKHEDE_STADIUM = create_stadium_config("Wankhede Stadium", 8, 3, 4)
WEMBLEY_STADIUM = create_stadium_config("Wembley Stadium", 12, 6, 8)

STADIUM_MAP = {
    "modi": NARENDRA_MODI_STADIUM,
    "wankhede": WANKHEDE_STADIUM,
    "wembley": WEMBLEY_STADIUM
}

if __name__ == "__main__":
    import json
    # Print Narendra Modi schema for verification
    print(json.dumps(NARENDRA_MODI_STADIUM.model_json_schema(), indent=2))
