"""
Venue Registry: Static Infrastructure Metadata.

Defines the physical characteristics of supported stadium venues.
"""

from typing import Dict
from src.core.models import StadiumConfig, Section, Gate, ConcessionBlock


def create_stadium_venue(
    name: str, section_count: int, gate_count: int, concession_count: int
) -> StadiumConfig:
    """Venue Factory: Generates a deterministic layout."""
    import math

    sections = []
    for i in range(1, section_count + 1):
        angle = (i / section_count) * 2 * math.pi
        sections.append(
            Section(
                section_id=f"S{i}",
                name=f"{name} Section {i}",
                capacity=int(120000 / section_count),
                x=200 + 150 * math.cos(angle),
                y=200 + 110 * math.sin(angle),
                adjacency_matrix={
                    f"S{j}": abs(i - j) * 20.0 for j in range(1, section_count + 1) if i != j
                },
            )
        )

    gates = [Gate(gate_id=f"G{i}", name=f"Gate {i}") for i in range(1, gate_count + 1)]
    concessions = [
        ConcessionBlock(block_id=f"C{i}", name=f"Food Stand {i}", category="Global")
        for i in range(1, concession_count + 1)
    ]

    return StadiumConfig(
        stadium_name=name, sections=sections, gates=gates, concession_blocks=concessions
    )


NARENDRA_MODI_STADIUM = create_stadium_venue("Narendra Modi Stadium", 10, 4, 6)
WANKHEDE_STADIUM = create_stadium_venue("Wankhede Stadium", 8, 3, 4)
WEMBLEY_STADIUM = create_stadium_venue("Wembley Stadium", 12, 6, 8)

STADIUM_MAP: Dict[str, StadiumConfig] = {
    "modi": NARENDRA_MODI_STADIUM,
    "wankhede": WANKHEDE_STADIUM,
    "wembley": WEMBLEY_STADIUM,
}
