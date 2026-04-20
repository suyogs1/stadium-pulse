"""
Optimizer Agent Module: Orchestrating Autonomous Crowd Management.

This module provides the OptimizerAgent which interprets stadium telemetry
to identify infrastructure bottlenecks and select the optimal operational play,
utilizing Gemini 1.5 Flash for high-congestion scenarios.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.core.models import StadiumConfig, StadiumState, OptimizerAction
from src.core.settings import settings
from src.services.gemini_service import gemini_service
from src.services.bigquery_service import bq_service
from src.services.logging_service import cloud_logger

# Configure diagnostic logging
optimizer_logger: logging.Logger = logging.getLogger("StadiumPulse.Optimizer")


class OptimizerAgent:
    """
    Strategic Orchestrator for Stadium Crowd Management.

    Interprets data from PulseAgent and identifies the optimal Operational Play
    by balancing crowd density variance and incentive budgets.
    """

    def __init__(
        self,
        stadium_config: StadiumConfig,
        max_incentives_budget: int = settings.INCENTIVE_BUDGET_HOURLY,
    ) -> None:
        """
        Initializes the OptimizerAgent.

        Args:
            stadium_config: Static configuration of the stadium venue.
            max_incentives_budget: Maximum hourly budget for discount-based incentives.
        """
        self.config: StadiumConfig = stadium_config
        self.max_incentives_budget: int = max_incentives_budget
        self.budget_remaining: int = max_incentives_budget
        self.budget_reset_time: datetime = datetime.now() + timedelta(hours=1)
        self.adjacency_map: Dict[str, Dict[str, float]] = {
            s.section_id: s.adjacency_matrix for s in stadium_config.sections
        }

    def _check_budget_reset(self) -> None:
        """Resets the incentive budget if the refresh window has passed."""
        if datetime.now() > self.budget_reset_time:
            self.budget_remaining = self.max_incentives_budget
            self.budget_reset_time = datetime.now() + timedelta(hours=1)
            optimizer_logger.info(
                "Optimizer: Incentive budget refreshed for the new operational window."
            )

    def evaluate_plays(self, current_state: StadiumState, event_id: Optional[str] = None) -> str:
        """
        Orchestrates the strategic analysis loop for stadium crowd management.
        """
        self._check_budget_reset()

        # 1. Scanning & Bottleneck Detection
        peak, occupancy, overcrowded, gates, food = self._identify_bottlenecks(current_state)
        reasoning_steps: List[str] = [
            "Phase 1: Ingesting realtime StadiumState and AdjacencyMatrix.",
            "Phase 2: Goal Initialization -> 1. Minimizing Crowd Density Variance.",
            f"Phase 3: Scanning for infrastructure bottlenecks (Peak Load: {peak:.1%}).",
        ]

        # 2. Decision Logic Initial State
        action_type, is_ai, reasoning_id, ai_meta = "MONITOR_ONLY", False, None, None

        # 3. Gemini AI Pathway
        if peak > settings.CONGESTION_ALERT_THRESHOLD and settings.ENABLE_AI_REASONING:
            action_type, is_ai, reasoning_id, ai_meta = self._get_ai_strategic_recommendation(
                current_state, peak, occupancy, event_id, reasoning_steps
            )

        # 4. Tactical Safety Fallbacks
        target_entities: List[str] = []
        if action_type == "MONITOR_ONLY":
            action_type, target_entities = self._apply_safety_heuristics(
                overcrowded, gates, food, reasoning_steps
            )
        else:
            # AI targets
            target_entities = overcrowded[:2]

        # 5. Persistence & Serialized Return
        return self._finalize_operational_play(
            occupancy,
            peak,
            action_type,
            target_entities,
            reasoning_steps,
            is_ai,
            reasoning_id,
            ai_meta,
            event_id,
        )

    def _identify_bottlenecks(self, state: StadiumState):
        """Identifies pressure points across infrastructure layers."""
        gates = [
            g
            for g, w in state.wait_times.items()
            if w > settings.WAIT_TIME_THRESHOLD_MINUTES and g.startswith("G")
        ]
        food = [f for f, w in state.wait_times.items() if w > 10.0 and f.startswith("C")]

        peak, occupancy, overcrowded = 0.0, {}, []
        for section in self.config.sections:
            load = state.occupancy.get(section.section_id, 0) / section.capacity
            occupancy[section.section_id], peak = load, max(peak, load)
            if load > settings.CONGESTION_ALERT_THRESHOLD:
                overcrowded.append(section.section_id)
        return peak, occupancy, overcrowded, gates, food

    def _get_ai_strategic_recommendation(self, state, peak, occ_map, event_id, trace):
        """Engages Gemini for high-congestion scenarios."""
        reason_id = f"GMN-{uuid.uuid4().hex[:8].upper()}"
        trace.append(f"ALERT: Threshold breached ({peak:.1%}). Engaging Gemini Service...")

        insight = gemini_service.execute_strategic_analysis(
            {
                "peak_load": peak,
                "occupancy_perc": occ_map,
                "wait_times": state.wait_times,
                "reasoning_tag": reason_id,
                "event_ref": event_id,
            }
        )
        trace.append(f"GEMINI_SERVICE Trace: {insight}")

        action = "MONITOR_ONLY"
        if "Predictive Buffer" in insight:
            action = "PREDICTIVE_BUFFER"
        elif "Direct Reroute" in insight:
            action = "REROUTE"
        elif "Incentive" in insight:
            action = "INCENTIVIZE"

        obs, anl = "Threshold Breach", "Capacity mismatch."
        if "REASONING:" in insight:
            parts = insight.split("STRATEGY:")
            obs_anl = parts[0].replace("REASONING:", "").strip()
            obs = obs_anl[: obs_anl.find(".") + 1] if "." in obs_anl else obs_anl
            anl = obs_anl[len(obs) :].strip() if len(obs_anl) > len(obs) else obs_anl

        ai_meta = {
            "observation": obs or "High density load.",
            "analysis": anl or "Multi-node risks.",
            "decision": action,
            "strategy": "System-Wide Redistribution",
        }
        return action, True, reason_id, ai_meta

    def _apply_safety_heuristics(self, overcrowded, gates, food, trace):
        """Applies tactical logic when AI is inactive or recommends monitoring."""
        action, targets = "MONITOR_ONLY", []
        if overcrowded:
            trace.append(f"Observation: Critical overcrowding in {overcrowded}.")
            action, targets = "PREDICTIVE_BUFFER", list(overcrowded)
        elif gates:
            trace.append(f"Observation: High wait times at gates: {gates}.")
            action = "REROUTE"
            for g_id in gates:
                alts = [g.gate_id for g in self.config.gates if g.gate_id != g_id]
                targets.append(f"{g_id}->{alts[0]}" if alts else g_id)
                if not alts:
                    trace.append("No alternative gates available.")
        elif food:
            trace.append(f"Observation: Queues at concessions: {food}.")
            cost = len(food) * 10
            if self.budget_remaining >= cost:
                action, targets, self.budget_remaining = (
                    "INCENTIVIZE",
                    list(food),
                    self.budget_remaining - cost,
                )
            else:
                trace.append("Budget exhausted. Falling back to MONITOR_ONLY.")
        else:
            trace.append("Observation: All metrics nominal. MONITOR_ONLY strategy engaged.")
        return action, targets

    def process_congestion_event(self, event_data: Dict[str, Any]) -> None:
        """
        Processes a single congestion event received from the Pub/Sub pipeline.

        This method acts as the entry point for the event-driven architecture.
        """
        section_id = event_data.get("section_id")
        congestion_level = event_data.get("congestion_level", 0.0)
        event_id = event_data.get("event_id")

        optimizer_logger.info(
            "Optimizer: Processing event %s for section %s (Load: %.2f)",
            event_id,
            section_id,
            congestion_level,
        )

        # In a real event-driven scenario, we might want to perform a full
        # evaluation or just react to this specific bottleneck.
        # For this demonstration, we'll suggest a localized action based on heuristics.
        action = "MONITOR_ONLY"
        if congestion_level > settings.CONGESTION_ALERT_THRESHOLD:
            action = "REROUTE"  # Default tactic for specific section alerts

        # Persist to BigQuery
        bq_service.record_congestion_event(
            section_id=section_id,
            load_factor=congestion_level,
            strategy=action,
            event_id=event_id,
        )

        # Log to Cloud Logging
        cloud_logger.log_event(
            agent_name="OptimizerAgent",
            action="EventProcessed",
            status="SUCCESS",
            metadata={
                "event_id": event_id,
                "section_id": section_id,
                "action": action,
            },
        )

        # Dispatch real-time intervention if needed
        if action != "MONITOR_ONLY":
            from src.agents.messenger_agent import MessengerAgent

            MessengerAgent().dispatch_alert(action_type=action, target_entities=[section_id])

    def _finalize_operational_play(
        self, occ_map, peak, action, targets, trace, is_ai, r_id, ai_meta, event_id
    ) -> str:
        """Records the decision and returns serialized action."""
        for s_id, load in occ_map.items():
            if load > 0.80:
                bq_service.record_congestion_event(
                    s_id, load, action if s_id in targets else "NONE", event_id=event_id
                )

        cloud_logger.log_event(
            agent_name="OptimizerAgent",
            action="StrategySelection",
            status="SUCCESS",
            metadata={"action": action, "is_ai": is_ai, "peak": round(peak, 4), "event": event_id},
        )

        return OptimizerAction(
            action_type=action,
            target_entities=targets,
            reasoning_trace=trace,
            budget_remaining=self.budget_remaining,
            is_ai_decision=is_ai,
            reasoning_id=r_id,
            ai_metadata=ai_meta,
        ).model_dump_json(indent=2)
