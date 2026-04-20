#!/bin/sh
echo "Launching StadiumPulse System Console..."

# 2. Launch Streamlit Dashboard (Headless for Cloud Run)
streamlit run src/ui/dashboard.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true
