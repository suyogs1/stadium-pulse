import pytest
from unittest.mock import patch
from src.main import main


@pytest.mark.asyncio
async def test_main_execution_loop():
    """Verify that the main CLI entrypoint correctly initializes and runs a loop iteration."""
    # We patch run_forever logic or similar if it exists
    # Or just patch execute_simulation_pass and make it raise a KeyboardInterrupt to exit the loop
    with patch(
        "src.main.StadiumPulseSimulationApp.execute_simulation_pass",
        side_effect=[None, KeyboardInterrupt],
    ):
        with patch("asyncio.sleep", return_value=None):
            try:
                await main()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                # Catch any unhandled errors in main
                pytest.fail(f"Main execution failed: {e}")


@pytest.mark.asyncio
async def test_main_cli_error_handling():
    """Verify that main handles unexpected errors during simulation passes."""
    with patch(
        "src.main.StadiumPulseSimulationApp.execute_simulation_pass",
        side_effect=[RuntimeError("Sim Crash"), KeyboardInterrupt],
    ):
        with patch("asyncio.sleep", return_value=None):
            try:
                await main()
            except KeyboardInterrupt:
                pass
            except Exception:
                pytest.fail("Main should handle errors gracefully and continue or exit safely.")
