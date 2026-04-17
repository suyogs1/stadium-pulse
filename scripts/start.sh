#!/bin/sh
# StadiumPulse Application Entrypoint
# This script ensures system stability by running the test suite 
# before launching the primary application service.

echo "Initiating StadiumPulse Autonomous Startup Sequence..."

# 1. Run Pre-flight Tests
python scripts/run_tests.py
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pre-flight tests failed. Startup sequence aborted."
    exit 2
fi

echo "Pre-flight checks passed. Launching system console..."

# 2. Launch Streamlit Dashboard (Default)
streamlit run src/app.py --server.port=8080 --server.address=0.0.0.0
