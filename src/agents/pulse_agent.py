"""
Pulse Agent Module: Real-time State Scanning and Anomaly Detection.

This module provides the PulseAgent class which monitors the stadium
filesystem for state updates and identifies statistical anomalies
in crowd distribution based on historical baselines.
"""

import os
import json
from typing import Dict, List, Any
from src.core.models import StadiumState
from src.services.logging_service import cloud_logger
from src.services.pubsub_service import pubsub_service


class PulseAgent:
    """
    Monitors and parses the physical state of the stadium from data files.

    Acts as the primary data ingestion agent for the StadiumPulse ecosystem.
    """

    def __init__(self, state_file_path: str) -> None:
        """
        Initializes the PulseAgent with a target state file.

        Args:
            state_file_path: Absolute or relative path to the state JSON file.
        """
        self.state_file_path: str = state_file_path

    def scan_stadium_state(self) -> StadiumState:
        """
        Loads the current stadium metrics and publishes events to the GCP pipeline.

        Returns:
            A StadiumState object representing current occupancy and wait times.
        """
        if not os.path.exists(self.state_file_path):
            return StadiumState(occupancy={}, wait_times={})

        with open(self.state_file_path, "r") as state_file:
            state_data: Dict[str, Any] = json.load(state_file)
            state: StadiumState = StadiumState(**state_data)

            # --- Event-Driven Pipeline Segment ---
            # Pulse Agent -> Pub/Sub: Streaming real-time telemetry
            for section_id, headcount in state.occupancy.items():
                if headcount > 1000:  # Threshold for event publishing
                    pubsub_service.publish_congestion_event(
                        section_id=section_id,
                        occupancy=headcount,
                        capacity=13000,  # Simulated avg capacity
                    )

            # Log pulse detection to the audit layer
            cloud_logger.log_event(
                agent_name="PulseAgent",
                action="PulseDetected",
                status="SUCCESS",
                metadata={
                    "occupancy_avg": (
                        sum(state.occupancy.values()) / len(state.occupancy)
                        if state.occupancy
                        else 0
                    )
                },
            )
            return state

    def detect_anomalies(
        self, current_state: StadiumState, historical_baseline: Dict[str, float]
    ) -> List[str]:
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
            current_occupancy: int = current_state.occupancy.get(section_id, 0)
            current_percentage: float = current_occupancy / 13000.0

            variance: float = abs(current_percentage - expected_percentage)
            if variance > 0.3:
                anomalies.append(section_id)

        if anomalies:
            cloud_logger.log_event(
                agent_name="PulseAgent",
                action="AnomaliesDetected",
                status="ALERT",
                metadata={"count": len(anomalies), "sections": anomalies},
            )

        return anomalies
