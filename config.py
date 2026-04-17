import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# --- Security & API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STADIUM_API_KEY = os.getenv("STADIUM_API_KEY", "pulse-secret-default")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "stadium-pulse-dev")

if not GEMINI_API_KEY:
    # We don't raise an error here to allow the app to start in 'Simulation Mode'
    # but we will handle it in the services layer if a real model call is attempted.
    pass


class Section(BaseModel):
    """
    Represents a discrete seating section within a stadium venue.
    
    Attributes:
        section_id: Unique string identifier for the section (e.g., 'S1').
        name: Human-readable name of the section.
        capacity: Maximum number of fans the section can hold.
        adjacency_matrix: Mapping of neighboring sections to their relative distance in meters.
    """
    section_id: str = Field(..., description="Unique identifier for the section")
    name: str = Field(..., description="Display name of the section")
    capacity: int = Field(..., description="Maximum seating capacity")
    x: float = Field(0.0, description="X coordinate for mapping (0-400)")
    y: float = Field(0.0, description="Y coordinate for mapping (0-400)")
    adjacency_matrix: Dict[str, float] = Field(
        ...,
        description="Distance in meters to other sections (section_id -> distance)"
    )


class Gate(BaseModel):
    """
    Represents an entry/exit portal for the stadium.
    
    Attributes:
        gate_id: Unique string identifier for the gate (e.g., 'G1').
        name: Human-readable name of the gate.
    """
    gate_id: str = Field(..., description="Unique identifier for the gate")
    name: str = Field(..., description="Display name of the gate")


class ConcessionBlock(BaseModel):
    """
    Represents a food, beverage, or retail point-of-sale area.
    
    Attributes:
        block_id: Unique string identifier for the block (e.g., 'C1').
        name: Human-readable name of the concession.
        category: The type of service provided (e.g., 'Snacks', 'Global').
    """
    block_id: str = Field(..., description="Unique identifier for the concession block")
    name: str = Field(..., description="Display name of the concession")
    category: str = Field(..., description="Type of concession (e.g., Snacks, Beverages)")


class StadiumConfig(BaseModel):
    """
    A comprehensive static definition of a stadium venue infrastructure.
    
    Attributes:
        stadium_name: Official name of the venue.
        sections: List of all seating sections.
        gates: List of all entry/exit gates.
        concession_blocks: List of all concession areas.
    """
    model_config = ConfigDict(title="Stadium Configuration Schema")

    stadium_name: str
    sections: List[Section]
    gates: List[Gate]
    concession_blocks: List[ConcessionBlock]


class StadiumState(BaseModel):
    """
    Encapsulates the dynamic, real-time metrics of a stadium's operational state.
    
    Attributes:
        occupancy: Current fan count for each section_id.
        wait_times: Estimated minutes of delay for each gate_id or block_id.
    """
    occupancy: Dict[str, int] = Field(
        default_factory=dict,
        description="Real-time occupancy per section"
    )
    wait_times: Dict[str, float] = Field(
        default_factory=dict,
        description="Real-time wait times in minutes"
    )


# --- Factory for Stadium Configurations ---

def create_stadium_venue(name: str, section_count: int, gate_count: int, concession_count: int) -> StadiumConfig:
    """
    Generates a structured StadiumConfig with generated IDs and adjacency patterns.
    
    Args:
        name: The name of the stadium.
        section_count: Number of sections to generate.
        gate_count: Number of gates to generate.
        concession_count: Number of concession blocks to generate.
        
    Returns:
        A populated StadiumConfig object.
    """
    import math
    sections: List[Section] = []
    for i in range(1, section_count + 1):
        section_id = f"S{i}"
        
        # Architectural Layout Logic
        if "Wembley" in name:
            # Rectangular-Oval
            angle = (i / section_count) * 2 * math.pi
            x = 200 + 150 * math.cos(angle)
            y = 200 + 110 * math.sin(angle)
        elif "Modi" in name:
            # Huge Ellipse
            angle = (i / section_count) * 2 * math.pi
            x = 200 + 160 * math.cos(angle)
            y = 200 + 150 * math.sin(angle)
        else:
            # Simple Circle
            angle = (i / section_count) * 2 * math.pi
            x = 200 + 130 * math.cos(angle)
            y = 200 + 130 * math.sin(angle)

        adj = {f"S{j}": abs(i - j) * 20.0 for j in range(1, section_count + 1) if i != j}
        sections.append(Section(
            section_id=section_id,
            name=f"{name} Section {i}",
            capacity=int(120000 / section_count), 
            x=x, y=y,
            adjacency_matrix=adj
        ))

    gates = [Gate(gate_id=f"G{i}", name=f"Gate {i}") for i in range(1, gate_count + 1)]
    concessions = [
        ConcessionBlock(block_id=f"C{i}", name=f"Food Stand {i}", category="Global") 
        for i in range(1, concession_count + 1)
    ]

    return StadiumConfig(
        stadium_name=name,
        sections=sections,
        gates=gates,
        concession_blocks=concessions
    )


# --- Pre-defined Global Venues ---

NARENDRA_MODI_STADIUM = create_stadium_venue("Narendra Modi Stadium", 10, 4, 6)
WANKHEDE_STADIUM = create_stadium_venue("Wankhede Stadium", 8, 3, 4)
WEMBLEY_STADIUM = create_stadium_venue("Wembley Stadium", 12, 6, 8)

STADIUM_MAP: Dict[str, StadiumConfig] = {
    "modi": NARENDRA_MODI_STADIUM,
    "wankhede": WANKHEDE_STADIUM,
    "wembley": WEMBLEY_STADIUM
}

if __name__ == "__main__":
    import json
    # Export Narendra Modi configuration schema for structural validation
    print(json.dumps(NARENDRA_MODI_STADIUM.model_json_schema(), indent=2))
