from datetime import datetime, timedelta
from typing import Dict, List
from pydantic import BaseModel, Field
from config import StadiumState, StadiumConfig
from services.gemini_reasoner import gemini_ai

class OptimizerAction(BaseModel):
    """Structured JSON object for the reasoning trace and action output."""
    action_type: str = Field(..., description="Action: REROUTE, INCENTIVIZE, PREDICTIVE_BUFFER, MONITOR_ONLY")
    target_entities: List[str] = Field(default_factory=list)
    reasoning_trace: List[str] = Field(default_factory=list)
    budget_remaining: int = Field(...)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class OptimizerAgent:
    """Intelligent agent that evaluates real-time stadium states."""
    def __init__(self, config: StadiumConfig, max_incentives_budget: int = 100):
        self.config = config
        self.max_incentives_budget = max_incentives_budget
        self.budget_remaining = max_incentives_budget
        self.budget_reset_time = datetime.now() + timedelta(hours=1)
        self.adjacency_matrix = {s.section_id: s.adjacency_matrix for s in config.sections}
        
    def _check_budget_reset(self):
        if datetime.now() >= self.budget_reset_time:
            self.budget_remaining = self.max_incentives_budget
            self.budget_reset_time = datetime.now() + timedelta(hours=1)

    def evaluate_plays(self, state: StadiumState) -> str:
        self._check_budget_reset()
        reasoning, target_entities = [], []
        action_type = "MONITOR_ONLY"

        reasoning.append("Phase 1: Ingesting realtime StadiumState and AdjacencyMatrix.")
        reasoning.append("Phase 2: Goal Initialization -> 1. Minimizing Crowd Density Variance. 2. Preserving the Incentive Budget.")
        reasoning.append("Phase 3: Scanning for bottlenecks.")

        high_wait_gates = [g for g, w in state.wait_times.items() if w > 15.0 and g.startswith('G')]
        high_wait_concessions = [c for c, w in state.wait_times.items() if w > 10.0 and c.startswith('C')]
        overcrowded = [s.section_id for s in self.config.sections if state.occupancy.get(s.section_id, 0) > (s.capacity * 0.9)]

        # --- Gemini AI Strategic Reasoning (Triggered only if > 85% congestion) ---
        max_load = 0
        occupancy_perc_map = {}
        for s in self.config.sections:
            perc = state.occupancy.get(s.section_id, 0) / s.capacity
            occupancy_perc_map[s.section_id] = perc
            max_load = max(max_load, perc)

        if max_load > 0.85:
            reasoning.append(f"ALERT: Infrastructure threshold breached ({max_load:.1%}). Engaging Gemini 1.5 Flash...")
            gemini_insight = gemini_ai.get_strategic_play({"occupancy_perc": occupancy_perc_map, "wait_times": state.wait_times})
            reasoning.append(f"GEMINI_REASONER Output: {gemini_insight}")

        if overcrowded:
            reasoning.append(f"Observation: Critical overcrowding in {overcrowded}.")
            action_type = "PREDICTIVE_BUFFER"
            target_entities.extend(overcrowded)
        elif high_wait_gates:
            reasoning.append(f"Observation: High wait times at gates: {high_wait_gates}.")
            action_type = "REROUTE"
            for gate_id in high_wait_gates:
                alts = [g.gate_id for g in self.config.gates if g.gate_id not in high_wait_gates]
                if alts:
                    target_entities.append(f"{gate_id}->{alts[0]}")
                else:
                    target_entities.append(gate_id)
                    reasoning.append(f"Decision: No alternative gates available for {gate_id}. Recommending buffer instead.")
        elif high_wait_concessions:
            reasoning.append(f"Observation: Queues at concessions: {high_wait_concessions}.")
            if self.budget_remaining >= (len(high_wait_concessions) * 10):
                action_type = "INCENTIVIZE"
                target_entities.extend(high_wait_concessions)
                self.budget_remaining -= (len(high_wait_concessions) * 10)
            else:
                reasoning.append("Incentive budget exhausted.")
        else:
            reasoning.append("Observation: All metrics are nominal. Current trend is stable; thresholds not breached.")
            reasoning.append("Decision: Executing MONITOR_ONLY strategy. Saving credits for the final whistle rush to prioritize Preserving the Incentive Budget.")

        return OptimizerAction(
            action_type=action_type,
            target_entities=target_entities,
            reasoning_trace=reasoning,
            budget_remaining=self.budget_remaining
        ).model_dump_json(indent=2)
