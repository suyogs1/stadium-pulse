"""
StadiumPulse Quality Assurance Runner.

This script executes the critical test suite for the StadiumPulse 
agentic orchestration cluster. It is designed to run in CI/CD 
pipelines and as a pre-flight check for Cloud Run deployments.
"""

import subprocess
import sys
import os

def run_tests():
    """Executes pytest and handles the evaluation of system stability."""
    print("=" * 60)
    print("STADIUMPULSE: PRE-FLIGHT SYSTEM QUALITY CHECK")
    print("=" * 60)
    
    # Set the working directory to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print(f"Running test suite in {project_root}...")
    
    try:
        # Prepare environment with PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

        # Execute pytest with coverage and summary detail
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--disable-warnings", "--cov=src", "--cov-report=term-missing"],
            env=env,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("PASSED: StadiumPulse core agents are STABLE.")
            print("=" * 60)
            return True
        else:
            print("\n" + "!" * 60)
            print("FAILED: Core system instability detected. Aborting startup.")
            print("!" * 60)
            return False
            
    except Exception as e:
        print(f"Encountered unexpected runner error: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
    sys.exit(0)
