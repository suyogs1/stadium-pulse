"""
Pulse Agent: Real-time State Scanning and Anomaly Detection.

This module monitors the stadium filesystem for state updates and 
identifies statistical anomalies in crowd distribution.
"""

import os
import json
from typing import Dict, List, Optional
from config import StadiumState

class PulseAgent:
    """
    Monitors and parses the physical state of the stadium from data files.
    """
    
    def __init__(self, state_file_path: str):
        """
        Initializes the PulseAgent with a target state file.
        
        Args:
            state_file_path: Absolute or relative path to the state JSON file.
        """
        self.state_file_path = state_file_path
        
    def scan_stadium_state(self) -> StadiumState:
        """
        Loads the current stadium metrics from the filesystem.
        
        Returns:
            A StadiumState object representing the current occupancy and wait times.
            Returns an empty StadiumState if the file does not exist.
        """
        if not os.path.exists(self.state_file_path):
            return StadiumState(occupancy={}, wait_times={})
            
        with open(self.state_file_path, 'r') as state_file:
            state_data = json.load(state_file)
            return StadiumState(**state_data)

    def detect_anomalies(self, current_state: StadiumState, historical_baseline: Dict[str, float]) -> List[str]:
        """
        Identifies sections with significant occupancy variance from historical norms.
        
        Args:
            current_state: The real-time StadiumState.
            historical_baseline: A mapping of section IDs to expected occupancy percentages.
            
        Returns:
            A list of section IDs exhibiting an anomaly (>=30% variance).
        """
        anomalies: List[str] = []
        for section_id, expected_percentage in historical_baseline.items():
            current_occupancy = current_state.occupancy.get(section_id, 0)
            # Baseline capacity normalization factor (13,000 avg)
            current_percentage = current_occupancy / 13000.0
            
            variance = abs(current_percentage - expected_percentage)
            if variance > 0.3:
                anomalies.append(section_id)
        return anomalies
