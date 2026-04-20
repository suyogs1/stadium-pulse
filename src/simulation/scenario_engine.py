"""
Scenario Engine Module: Synthetic Data Generation and Stress Testing.

This module provides the ScenarioEngine class to simulate complex
stadium crowd patterns, allowing for deterministic testing of
autonomous agents under various stress scenarios (e.g., half-time rushes).
"""

import random
from typing import Dict
from src.core.models import StadiumConfig, StadiumState


class ScenarioEngine:
    """
    Simulates time-series crowd behavior and infrastructure pressure points.

    Generates synthetic StadiumState objects to drive simulation loops.
    """

    def __init__(self, venue_config: StadiumConfig) -> None:
        """
        Initializes the engine with a specific stadium configuration.

        Args:
            venue_config: Static metadata about sections, gates, and concessions.
        """
        self.venue_config: StadiumConfig = venue_config
        self.current_simulation_minute: int = 0

    def generate_nominal_state(self) -> StadiumState:
        """
        Creates a 'Normal' stadium state where all metrics are within safe limits.

        Returns:
            A StadiumState object with randomized but healthy metrics.
        """
        # Distribute occupancy randomly between 40% and 60% capacity
        current_occupancy: Dict[str, int] = {
            section.section_id: int(section.capacity * random.uniform(0.4, 0.6))
            for section in self.venue_config.sections
        }

        # Set baseline wait times (low congestion)
        initial_wait_times: Dict[str, float] = {
            gate.gate_id: random.uniform(2.0, 5.0) for gate in self.venue_config.gates
        }
        initial_wait_times.update(
            {
                block.block_id: random.uniform(1.0, 4.0)
                for block in self.venue_config.concession_blocks
            }
        )

        return StadiumState(occupancy=current_occupancy, wait_times=initial_wait_times)

    def inject_congestion_spike(
        self, current_state: StadiumState, target_type: str, severity_count: int = 1
    ) -> StadiumState:
        """
        Artificially inflates load on specific stadium infrastructure modules.

        Args:
            current_state: The state object to modify.
            target_type: Category of infrastructure (concession, gate, section).
            severity_count: Number of targets to affects with high congestion.

        Returns:
            The modified StadiumState object.
        """
        if target_type == "concession":
            target_blocks = random.sample(self.venue_config.concession_blocks, severity_count)
            for block in target_blocks:
                current_state.wait_times[block.block_id] = random.uniform(15.0, 25.0)

        elif target_type == "gate":
            target_gates = random.sample(self.venue_config.gates, severity_count)
            for gate in target_gates:
                current_state.wait_times[gate.gate_id] = random.uniform(20.0, 40.0)

        elif target_type == "section":
            target_sections = random.sample(self.venue_config.sections, severity_count)
            for section in target_sections:
                current_state.occupancy[section.section_id] = int(
                    section.capacity * random.uniform(0.92, 0.98)
                )

        return current_state

    def simulate_simulation_step(self, elapsed_minutes: int) -> StadiumState:
        """
        Generates a state for a specific point in time in the simulation timeline.

        Args:
            elapsed_minutes: Minutes since start of the simulation.

        Returns:
            The calculated StadiumState for that specific moment.
        """
        state: StadiumState = self.generate_nominal_state()

        # Scenario Logic: Programmed deviations by time
        if elapsed_minutes == 2:
            # Half-time rush simulation: High concession load
            state = self.inject_congestion_spike(state, "concession", severity_count=2)
        elif elapsed_minutes == 4:
            # Post-peak optimization: Cooldown effect
            for key in state.wait_times:
                state.wait_times[key] *= 0.7

        return state
