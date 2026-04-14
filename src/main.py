import asyncio
import json
from datetime import datetime
import os
import sys

# Add project root and src to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "src"))

from config import NARENDRA_MODI_STADIUM
from src.agents.pulse_agent import PulseAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent
from src.services.google_services import bq_client

class StadiumPulseApp:
    def __init__(self):
        self.state_file = "current_stadium_state.json"
        self.pulse = PulseAgent(self.state_file)
        self.optimizer = OptimizerAgent(NARENDRA_MODI_STADIUM)
        self.messenger = MessengerAgent()

    async def run_simulation(self):
        print(f"--- StadiumPulse Simulation Started at {datetime.now()} ---")
        historical_averages = bq_client.fetch_historical_averages(15)
        print(f"[Core] Historical Baseline Ingested: {len(historical_averages)} sections retrieved.")
        
        current_state = self.pulse.scan_stadium_state()
        print(f"[Pulse] State scanned. Detected {len(current_state.occupancy)} active sections.")
        
        decision = json.loads(self.optimizer.evaluate_plays(current_state))
        print("\n[Reasoning Trace Output]:")
        for trace in decision["reasoning_trace"]: print(f"  > {trace}")
        
        if decision["action_type"] != "MONITOR_ONLY":
            print("[Messenger] Dispatching alerts...")
            self.messenger.dispatch_alert(decision["action_type"], decision["target_entities"])
        else:
            print("[Messenger] No action required.")

        print(f"\n[Feedback Loop] Waiting 3s...")
        await asyncio.sleep(3)
        print("[Status] RE-EVALUATE: Triggering secondary optimization pass.")
        print(f"\n--- Simulation Pass Finished at {datetime.now()} ---")

async def main():
    app = StadiumPulseApp()
    await app.run_simulation()

if __name__ == "__main__":
    asyncio.run(main())
