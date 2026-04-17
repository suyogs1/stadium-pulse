import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from config import StadiumConfig, StadiumState
from src.services.gemini_reasoner import gemini_ai

# Configure diagnostic logging
logger = logging.getLogger("StadiumPulse.Optimizer")

class OptimizerAction(BaseModel):
    """
    Structured response model for an optimization decision.
    """
    action_type: str = Field(..., description="Action: REROUTE, INCENTIVIZE, PREDICTIVE_BUFFER, MONITOR_ONLY")
    target_entities: List[str] = Field(default_factory=list)
    reasoning_trace: List[str] = Field(default_factory=list)
    budget_remaining: int = Field(...)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    is_ai_decision: bool = Field(default=False)
    reasoning_id: Optional[str] = Field(default=None)
    ai_metadata: Optional[Dict[str, str]] = Field(default=None)

class OptimizerAgent:
    """
    Orchestration Agent for Crowd Management.
    Interprets data from PulseAgent and identifies the optimal Operational Play.
    """
    
    def __init__(self, stadium_config: StadiumConfig, max_incentives_budget: int = 1000):
        self.config = stadium_config
        self.max_incentives_budget = max_incentives_budget
        self.budget_remaining = max_incentives_budget
        self.budget_reset_time = datetime.now() + timedelta(hours=1)
        self.adjacency_map = {s.section_id: s.adjacency_matrix for s in stadium_config.sections}

    def _check_budget_reset(self):
        """Resets the incentive budget if the refresh window has passed."""
        if datetime.now() > self.budget_reset_time:
            self.budget_remaining = self.max_incentives_budget
            self.budget_reset_time = datetime.now() + timedelta(hours=1)
            logger.info("Optimizer: Incentive budget refreshed for the new operational window.")

    def evaluate_plays(self, current_state: StadiumState) -> str:
        """
        Processes current stadium metrics and generates a strategic plan.
        """
        self._check_budget_reset()
        reasoning_steps: List[str] = []
        target_entities: List[str] = []
        action_type = "MONITOR_ONLY"
        is_ai = False
        reasoning_id = None
        ai_meta = None

        reasoning_steps.extend([
            "Phase 1: Ingesting realtime StadiumState and AdjacencyMatrix.",
            "Phase 2: Goal Initialization -> 1. Minimizing Crowd Density Variance. 2. Preserving the Incentive Budget.",
            "Phase 3: Scanning for infrastructure bottlenecks."
        ])

        # Core Heuristic Analysis
        high_wait_gates = [g_id for g_id, wait in current_state.wait_times.items() if wait > 15.0 and g_id.startswith('G')]
        high_wait_food = [c_id for c_id, wait in current_state.wait_times.items() if wait > 10.0 and c_id.startswith('C')]
        overcrowded_sections = [
            section.section_id for section in self.config.sections 
            if current_state.occupancy.get(section.section_id, 0) > (section.capacity * 0.9)
        ]

        # Calculate venue-wide load for AI trigger
        peak_occupancy_ratio = 0.0
        occupancy_map: Dict[str, float] = {}
        for section in self.config.sections:
            load_ratio = current_state.occupancy.get(section.section_id, 0) / section.capacity
            occupancy_map[section.section_id] = load_ratio
            peak_occupancy_ratio = max(peak_occupancy_ratio, load_ratio)

        # AI ORCHESTRATION PATHWAY
        if peak_occupancy_ratio > 0.85:
            is_ai = True
            reasoning_id = f"GMN-{uuid.uuid4().hex[:8].upper()}"
            reasoning_steps.append(f"ALERT: Infrastructure threshold breached ({peak_occupancy_ratio:.1%}). Engaging Gemini Engine...")
            
            ai_context = {
                "peak_load": peak_occupancy_ratio,
                "occupancy_perc": occupancy_map,
                "wait_times": current_state.wait_times,
                "reasoning_tag": reasoning_id
            }
            
            gemini_insight = gemini_ai.get_strategic_play(ai_context)
            reasoning_steps.append(f"GEMINI_REASONER Trace: {gemini_insight}")
            
            # Action Mapping
            if "Predictive Buffer" in gemini_insight: action_type = "PREDICTIVE_BUFFER"
            elif "Direct Reroute" in gemini_insight: action_type = "REROUTE"
            elif "Incentive" in gemini_insight: action_type = "INCENTIVIZE"
            
            # Metadata Construction
            obs = "Threshold Breach"
            anl = "Capacity mismatch across sectors."
            if "REASONING:" in gemini_insight:
                parts = gemini_insight.split("STRATEGY:")
                obs_anl = parts[0].replace("REASONING:", "").strip()
                obs = obs_anl[:obs_anl.find('.')+1] if '.' in obs_anl else obs_anl
                anl = obs_anl[len(obs):].strip() if len(obs_anl) > len(obs) else obs_anl
            
            ai_meta = {
                "observation": obs or "High density load detected.",
                "analysis": anl or "Multi-node congestion risks identified.",
                "decision": action_type,
                "strategy": "System-Wide Redistribution"
            }
            # For simplicity in this demo, targeting first 2 congested nodes
            target_entities = [s for s, l in occupancy_map.items() if l > 0.85][:2]

        # HEURISTIC FALLBACK PATHWAY (If AI not triggered or monitoring only)
        if action_type == "MONITOR_ONLY":
            if overcrowded_sections:
                reasoning_steps.append(f"Observation: Critical overcrowding in {overcrowded_sections}.")
                action_type = "PREDICTIVE_BUFFER"
                target_entities.extend(overcrowded_sections)
            elif high_wait_gates:
                reasoning_steps.append(f"Observation: High wait times at gates: {high_wait_gates}.")
                action_type = "REROUTE"
                for g_id in high_wait_gates:
                    alts = [g.gate_id for g in self.config.gates if g.gate_id != g_id]
                    if alts:
                        target_entities.append(f"{g_id}->{alts[0]}")
                    else:
                        target_entities.append(g_id)
                        reasoning_steps.append(f"Decision: No alternative gates available for {g_id}. Recommending buffer.")
            elif high_wait_food:
                reasoning_steps.append(f"Observation: Queues at concessions: {high_wait_food}.")
                incentive_cost = len(high_wait_food) * 10
                if self.budget_remaining >= incentive_cost:
                    action_type = "INCENTIVIZE"
                    target_entities.extend(high_wait_food)
                    self.budget_remaining -= incentive_cost
                else:
                    reasoning_steps.append("Incentive budget exhausted for this window.")
            else:
                reasoning_steps.append("Observation: All metrics are nominal. Trends are stable.")
                reasoning_steps.append("Decision: Executing MONITOR_ONLY strategy to preserve incentive budget.")

        # Final Budget Safeguard (Double Check)
        if action_type == "INCENTIVIZE" and self.budget_remaining < 50 and is_ai:
            reasoning_steps.append("WARNING: Budget exhaustion. Degrading to MONITOR_ONLY.")
            action_type = "MONITOR_ONLY"
            target_entities = []

        return OptimizerAction(
            action_type=action_type,
            target_entities=target_entities,
            reasoning_trace=reasoning_steps,
            budget_remaining=self.budget_remaining,
            is_ai_decision=is_ai,
            reasoning_id=reasoning_id,
            ai_metadata=ai_meta
        ).model_dump_json(indent=2)
