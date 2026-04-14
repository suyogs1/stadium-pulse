import asyncio
import json
import os
import sys
from datetime import datetime

# Add project root and src to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "src"))

from config import NARENDRA_MODI_STADIUM
from src.simulation.scenario_engine import ScenarioEngine
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent

async def run_timeline_simulation():
    print("="*60)
    print("STADIUMPULSE: 5-MINUTE CONGESTION TIMELINE SIMULATION")
    print("="*60)
    
    engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    optimizer = OptimizerAgent(NARENDRA_MODI_STADIUM)
    messenger = MessengerAgent()
    
    for minute in range(1, 6):
        print(f"\n[MINUTE {minute}] {datetime.now().strftime('%H:%M:%S')}")
        if minute == 1:
            state = engine.generate_nominal_state()
        elif minute == 2:
            state = engine.inject_spike(engine.generate_nominal_state(), "concession", count=1)
        elif minute == 3:
            state = engine.inject_spike(engine.generate_nominal_state(), "concession", count=1)
        elif minute == 4:
            state = engine.simulate_step(4)
        else:
            state = engine.generate_nominal_state()

        decision = json.loads(optimizer.evaluate_plays(state))
        print("\n--- AI REASONING LOG ---")
        for trace in decision['reasoning_trace']:
            print(f"  > {trace}")
        
        if decision['action_type'] != "MONITOR_ONLY":
            print(f"\n[Messenger] DISPATCH -> Type: {decision['action_type']} | Targets: {decision['target_entities']}")
            messenger.dispatch_alert(decision['action_type'], decision['target_entities'])
        
        await asyncio.sleep(2)

    print("\n[SIMULATION COMPLETE] 5-minute window concluded.")

if __name__ == "__main__":
    asyncio.run(run_timeline_simulation())
