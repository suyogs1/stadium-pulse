"""
Scenario Engine: Synthetic Data Generation and Stress Testing.

This module simulates stadium crowd patterns, allowing for deterministic 
testing of agentic reasoning under various stress scenarios (e.g., surges).
"""

import random
from typing import Dict, Any, List, Optional
from config import StadiumConfig, StadiumState

class ScenarioEngine:
    """
    Simulates time-series crowd behavior and infrastructure pressure points.
    """
    
    def __init__(self, venue_config: StadiumConfig):
        """
        Initializes the engine with a specific stadium configuration.
        """
        self.venue_config = venue_config
        self.current_simulation_minute = 0
        
    def generate_nominal_state(self) -> StadiumState:
        """
        Creates a 'Normal' stadium state where all metrics are healthy.
        
        Returns:
            A StadiumState object with randomized but safe values.
        """
        # Distribute occupancy randomly between 40% and 60% capacity
        current_occupancy = {
            section.section_id: int(section.capacity * random.uniform(0.4, 0.6)) 
            for section in self.venue_config.sections
        }
        
        # Set baseline wait times (low congestion)
        initial_wait_times = {gate.gate_id: random.uniform(2.0, 5.0) for gate in self.venue_config.gates}
        initial_wait_times.update({
            block.block_id: random.uniform(1.0, 4.0) 
            for block in self.venue_config.concession_blocks
        })
        
        return StadiumState(occupancy=current_occupancy, wait_times=initial_wait_times)

    def inject_congestion_spike(self, current_state: StadiumState, target_type: str, severity_count: int = 1) -> StadiumState:
        """
        Artificially inflates load on specific stadium infrastructure.
        
        Args:
            current_state: The state object to modify.
            target_type: Category of infrastructure (concession, gate, section).
            severity_count: Number of targets to infect with high congestion.
            
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
                current_state.occupancy[section.section_id] = int(section.capacity * random.uniform(0.92, 0.98))
                
        return current_state

    def simulate_simulation_step(self, elapsed_minutes: int) -> StadiumState:
        """
        Generates a state for a specific point in time in the simulation timeline.
        
        Args:
            elapsed_minutes: Minutes since start of the simulation.
            
        Returns:
            The calculated StadiumState for that moment.
        """
        state = self.generate_nominal_state()
        
        # Programmed scenario deviations
        if elapsed_minutes == 2:
            # Half-time rush simulation
            state = self.inject_congestion_spike(state, "concession", severity_count=2)
        elif elapsed_minutes == 4:
            # Post-peak optimization effect simulation (cooldown)
            for key in state.wait_times: 
                state.wait_times[key] *= 0.7
                
        return state
