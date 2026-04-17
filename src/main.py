"""
StadiumPulse CLI Entrypoint: Simulation Loop.

This module provides a command-line interface to run the agentic 
crowd management orchestration loop in a simulated environment.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add project root and src to path for consistent imports across environments
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from config import NARENDRA_MODI_STADIUM
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent
from src.services.google_services import bq_client

class StadiumPulseSimulationApp:
    """
    Main application coordinator for the CLI simulation environment.
    """
    
    def __init__(self):
        """
        Initializes agents and configuration for the Narendra Modi Stadium.
        """
        self.state_file_path = "current_stadium_state.json"
        self.pulse_agent = PulseAgent(self.state_file_path)
        self.optimizer_agent = OptimizerAgent(NARENDRA_MODI_STADIUM)
        self.messenger_agent = MessengerAgent()

    async def execute_simulation_pass(self):
        """
        Runs a single end-to-end iteration of the StadiumPulse agent loop:
        Scan -> Analyze -> Optimize -> Dispatch.
        """
        print(f"\n--- StadiumPulse Simulation Started at {datetime.now().strftime('%H:%M:%S')} ---")
        
        # 1. External Data Ingestion (BigQuery)
        historical_baseline = bq_client.fetch_historical_averages(match_minute=15)
        print(f"[Core] Historical Baseline Ingested: {len(historical_baseline)} sections retrieved.")
        
        # 2. Local State Scanning (Pulse Agent)
        current_state = self.pulse_agent.scan_stadium_state()
        print(f"[Pulse] State scanned. Detected {len(current_state.occupancy)} active stadium sections.")
        
        # 3. AI Strategic Reasoning (Optimizer Agent)
        optimization_json = self.optimizer_agent.evaluate_plays(current_state)
        decision_data = json.loads(optimization_json)
        
        print("\n[AI Reasoning Trace Output]:")
        for log_line in decision_data["reasoning_trace"]: 
            print(f"  > {log_line}")
        
        # 4. Intervention Dispatch (Messenger Agent)
        if decision_data["action_type"] != "MONITOR_ONLY":
            print(f"[Messenger] ALERT: Dispatching '{decision_data['action_type']}' intervention...")
            self.messenger_agent.dispatch_alert(
                action_type=decision_data["action_type"], 
                target_entities=decision_data["target_entities"]
            )
        else:
            print("[Messenger] Status: Nominal. No action dispatched.")

        print(f"\n[Environment] Waiting 3s for feedback loop cycle...")
        await asyncio.sleep(3)
        print(f"--- Simulation Pass Finished at {datetime.now().strftime('%H:%M:%S')} ---")

async def main():
    """Application entry point for simulation execution."""
    if "--dev" in sys.argv:
        from scripts.run_tests import run_tests
        if not run_tests():
            print("\nCRITICAL: System instability detected in Dev Mode. Aborting.")
            sys.exit(1)
            
    app = StadiumPulseSimulationApp()
    await app.execute_simulation_pass()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation terminated by user.")
