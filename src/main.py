"""
StadiumPulse CLI Entrypoint: Simulated Agentic Orchestration.

This module provides a command-line interface to run the autonomous
crowd management loop. It simulates the end-to-end flow:
Ingestion -> Scanning -> Strategic Reasoning -> Intervention Dispatch.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root and src to path for consistent imports across environments
root_path: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from src.core.venues import NARENDRA_MODI_STADIUM
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent
from src.services.bigquery_service import bq_service
from src.services.storage_service import storage_service


class StadiumPulseSimulationApp:
    """
    Main application coordinator for the CLI simulation environment.

    Orchestrates the lifecycle of active agents and manages the transition
    between data scanning and AI-driven optimization.
    """

    def __init__(self) -> None:
        """
        Initializes agents and static configuration for the environment.
        """
        self.state_file_path: str = "current_stadium_state.json"
        self.pulse_agent: PulseAgent = PulseAgent(self.state_file_path)
        self.optimizer_agent: OptimizerAgent = OptimizerAgent(NARENDRA_MODI_STADIUM)
        self.messenger_agent: MessengerAgent = MessengerAgent()

        # --- Event Pipeline Initialization ---
        # Pulse Agent -> Pub/Sub -> Optimizer
        from src.services.pubsub_service import pubsub_service

        pubsub_service.subscribe_to_telemetry(self.optimizer_agent.process_congestion_event)

    async def execute_simulation_pass(self) -> None:
        """
        Runs a single end-to-end iteration of the StadiumPulse agent loop.

        Execution Flow:
        1. Context Retrieval (BigQuery)
        2. Real-time Scanning (Pulse)
        3. Multi-agent Optimization (Gemini AI / Heuristics)
        4. Strategy Dispatch (Messenger)
        5. Cloud Archival (GCS)
        """
        print(f"\n--- StadiumPulse Simulation Started at {datetime.now().strftime('%H:%M:%S')} ---")

        # 1. External Data Ingestion (BigQuery Historical Context)
        historical_baseline: Dict[str, float] = bq_service.get_historical_baseline(
            offset_minutes=15
        )
        print(
            f"[Core] Historical Baseline Ingested: {len(historical_baseline)} sections retrieved."
        )

        # 2. Local State Scanning (Pulse Agent Telemetry)
        current_state = self.pulse_agent.scan_stadium_state()
        print(
            f"[Pulse] State scanned. Detected {len(current_state.occupancy)} active stadium sections."
        )

        # 3. AI Strategic Reasoning (Optimizer Agent Assessment)
        optimization_json: str = self.optimizer_agent.evaluate_plays(current_state)
        decision_data: Dict[str, Any] = json.loads(optimization_json)

        print("\n[AI Reasoning Trace Output]:")
        reasoning_trace_buffer: str = ""
        for log_line in decision_data["reasoning_trace"]:
            print(f"  > {log_line}")
            reasoning_trace_buffer += f"{log_line}\n"

        # 4. Intervention Dispatch (Messenger Agent Alerts)
        if decision_data["action_type"] != "MONITOR_ONLY":
            print(
                f"[Messenger] ALERT: Dispatching '{decision_data['action_type']}' intervention..."
            )
            self.messenger_agent.dispatch_alert(
                action_type=decision_data["action_type"],
                target_entities=decision_data["target_entities"],
            )
        else:
            print("[Messenger] Status: Nominal. No action dispatched.")

        # 5. Cloud Storage Integration: Archiving the Reasoning Trace
        log_name: str = f"sim_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        storage_service.upload_blob(reasoning_trace_buffer, log_name)

        print(f"\n[Cloud] Pass complete. GCS Log generated: {log_name}")
        print("[Environment] Waiting 3s for feedback loop cycle...")
        await asyncio.sleep(3)
        print(f"--- Simulation Pass Finished at {datetime.now().strftime('%H:%M:%S')} ---")


async def main() -> None:
    """Application entry point for simulation execution."""
    if "--dev" in sys.argv:
        from scripts.run_tests import run_tests

        if not run_tests():
            print("\nCRITICAL: System instability detected in Dev Mode. Aborting.")
            sys.exit(1)

    app: StadiumPulseSimulationApp = StadiumPulseSimulationApp()
    print("Starting continuous simulation loop (Press Ctrl+C to stop)...")
    while True:
        try:
            await app.execute_simulation_pass()
        except Exception as e:
            print(f"\n[ERROR] Simulation pass failed: {e}")
            print("Recovering for next cycle...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation terminated by user.")
