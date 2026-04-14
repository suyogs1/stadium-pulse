import random
from typing import Dict, Any, List
from config import StadiumConfig, StadiumState

class ScenarioEngine:
    """Generates synthetic congestion events and time-series data."""
    def __init__(self, config: StadiumConfig):
        self.config = config
        self.current_minute = 0
        
    def generate_nominal_state(self) -> StadiumState:
        """Generates a stable, healthy stadium occupancy state."""
        occupancy = {s.section_id: int(s.capacity * random.uniform(0.4, 0.6)) for s in self.config.sections}
        wait_times = {g.gate_id: random.uniform(2.0, 5.0) for g in self.config.gates}
        wait_times.update({c.block_id: random.uniform(1.0, 4.0) for c in self.config.concession_blocks})
        return StadiumState(occupancy=occupancy, wait_times=wait_times)

    def inject_spike(self, state: StadiumState, target_type: str, count: int = 1) -> StadiumState:
        """Injects a congestion spike into specific entities."""
        if target_type == "concession":
            targets = random.sample(self.config.concession_blocks, count)
            for t in targets: state.wait_times[t.block_id] = random.uniform(15.0, 25.0)
        elif target_type == "gate":
            targets = random.sample(self.config.gates, count)
            for t in targets: state.wait_times[t.gate_id] = random.uniform(20.0, 40.0)
        elif target_type == "section":
            targets = random.sample(self.config.sections, count)
            for t in targets: state.occupancy[t.section_id] = int(t.capacity * random.uniform(0.92, 0.98))
        return state

    def simulate_step(self, minute: int) -> StadiumState:
        state = self.generate_nominal_state()
        if minute == 2:
            state = self.inject_spike(state, "concession", count=2)
        elif minute == 4:
            for k in state.wait_times: state.wait_times[k] *= 0.7
        return state
