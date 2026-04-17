"""
Timeline Simulation: Time-Series Congestion Demonstration.

This script executes a 5-minute accelerated simulation of stadium 
crowd dynamics, showing how the orchestration agents react to 
evolving pressure points over a scheduled period.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add project root and src to path for consistent imports
current_script_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, "src"))

from config import NARENDRA_MODI_STADIUM
from src.simulation.scenario_engine import ScenarioEngine
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.messenger_agent import MessengerAgent

async def run_timeline_simulation() -> None:
    """
    Executes an autonomous 5-minute scenario loop with automated 
    congestion spikes and AI-driven remediations.
    """
    print("=" * 60)
    print("STADIUMPULSE: 5-MINUTE CONGESTION TIMELINE SIMULATION")
    print("=" * 60)
    
    # Initialize Core Service Cluster
    simulation_engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    optimization_agent = OptimizerAgent(NARENDRA_MODI_STADIUM)
    broadcast_agent = MessengerAgent()
    
    for current_minute in range(1, 6):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[MINUTE {current_minute}] Local Time: {timestamp}")
        
        # State Generation with specific injected scenarios per minute
        if current_minute == 1:
            state = simulation_engine.generate_nominal_state()
        elif current_minute == 2:
            state = simulation_engine.inject_congestion_spike(
                simulation_engine.generate_nominal_state(), 
                target_type="concession", 
                severity_count=1
            )
        elif current_minute == 3:
            state = simulation_engine.inject_congestion_spike(
                simulation_engine.generate_nominal_state(), 
                target_type="section", 
                severity_count=1
            )
        elif current_minute == 4:
            state = simulation_engine.simulate_simulation_step(elapsed_minutes=4)
        else:
            state = simulation_engine.generate_nominal_state()

        # Decision Execution Phase
        decision_raw = optimization_agent.evaluate_plays(state)
        decision_dict = json.loads(decision_raw)
        
        print("\n--- AI REASONING LOG ---")
        for trace_entry in decision_dict['reasoning_trace']:
            print(f"  > {trace_entry}")
        
        # Action Dispatch Phase
        if decision_dict['action_type'] != "MONITOR_ONLY":
            print(f"\n[Messenger] DISPATCH -> Type: {decision_dict['action_type']} | Targets: {decision_dict['target_entities']}")
            broadcast_agent.dispatch_alert(
                action_type=decision_dict['action_type'], 
                target_entities=decision_dict['target_entities']
            )
        else:
            print("\n[Messenger] System Stable. No dispatch required.")
        
        # Accelerated time step for demonstration speed
        await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("[SIMULATION COMPLETE] 5-minute window concluded.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(run_timeline_simulation())
    except KeyboardInterrupt:
        print("\nSimulation aborted.")
