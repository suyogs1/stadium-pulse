import os
from typing import Dict, List
from config import StadiumState

class PulseAgent:
    """Agent responsible for scanning real-time state files."""
    
    def __init__(self, state_file_path: str):
        self.state_file_path = state_file_path
        
    def scan_stadium_state(self) -> StadiumState:
        """Reads and parses the current stadium state from disk."""
        if not os.path.exists(self.state_file_path):
            # Return empty state if file doesn't exist yet
            return StadiumState(occupancy={}, wait_times={})
            
        import json
        with open(self.state_file_path, 'r') as f:
            data = json.load(f)
            return StadiumState(**data)

    def detect_anomalies(self, current_state: StadiumState, baseline: Dict[str, float]) -> List[str]:
        """
        Compares current occupancy against historical baseline.
        Returns a list of section_ids that show ≥30% variance (anomaly).
        """
        anomalies = []
        for section_id, historical_perc in baseline.items():
            current_count = current_state.occupancy.get(section_id, 0)
            current_perc = current_count / 13000.0
            
            if abs(current_perc - historical_perc) > 0.3:
                anomalies.append(section_id)
        return anomalies
