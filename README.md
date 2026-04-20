# 📡 StadiumPulse: AI Crowd Orchestration System

[![Quality Gate](https://github.com/suyogs1/stadium-pulse/actions/workflows/tests.yml/badge.svg)](https://github.com/suyogs1/stadium-pulse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**StadiumPulse** is an agentic AI platform designed to transform high-density stadium environments from *Chaos to Calm*. Using a multi-agent cluster powered by **Gemini 1.5 Flash**, the system autonomously identifies occupancy bottlenecks and dispatches real-time interventions to ensure fan safety and operational efficiency.

---

## 🚀 Why This Matters
StadiumPulse isn't just a dashboard; it's a **safety-critical orchestration engine** with massive real-world impact:
*   **🔹 Dynamic Safety**: Proactively mitigates "crush" risks by identifying density spikes *before* they reach critical levels.
*   **🔹 Operational Excellence**: Projects a **30% reduction in wait times** at gates and concessions via intelligent load balancing.
*   **🔹 Multi-Industry Scale**: Instantly portable to **airports, metro hubs, and theme parks**.

---

---

## ☁️ Google Cloud Integration: The Intelligence Layer
StadiumPulse is built natively on **Google Cloud Platform (GCP)**, utilizing the most advanced AI and data services to ensure safety-critical reliability.

### 🧠 AI Reasoning with Gemini 1.5 Flash
The **Gemini Service** acts as the platform's strategic cortex. When the Pulse Agent detects critical congestion (>85%), the system engages Gemini to perform **Spatial Strategic Analysis**. It evaluates adjacency maps and historical patterns to recommend the optimal operational play (e.g., Predictive Buffering vs. Rerouting).

### 📊 Post-Match Analytics with BigQuery
Every density spike and autonomous decision is streamed into **BigQuery**. This creates a high-fidelity historical audit trail, allowing stadium operators to perform post-match analysis, refine evacuation models, and train local predictive heuristics.

### 📡 Observability via Cloud Logging
The entire multi-agent loop—from pulse detection to alert dispatch—is monitored via **Google Cloud Logging**. This provides centralized observability and allows for real-time alerting on system health and agentic performance.

### 🏗️ Technical Architecture
```mermaid
graph TD
    subgraph "Stadium Ingress (IoT/Edge)"
        sensors[IoT Sensors] --> pulse[Pulse Agent]
    end

    subgraph "Google Cloud Intelligence"
        pulse --> |Telemetry| logging[Cloud Logging]
        pulse --> |Current State| opt[Optimizer Agent]
        opt --> |Strategic Query| gemini[Gemini 1.5 Flash]
        opt --> |Decision Persistence| bq[BigQuery]
    end

    subgraph "Intervention (Dispatch)"
        opt --> |Strategy| msg[Messenger Agent]
        msg --> |Broadcast| signage[Digital Signage / Mobile App]
    end
```

---

## 📸 Demo Preview: 5-Second Clarity

| 📡 Orchestration Console | 🧠 Strategic AI Reasoning | 🗺️ Geospatial Heatmap |
| :--- | :--- | :--- |
| ![Dashboard Overview](docs/screenshots/dashboard_view.png) | ![AI Reasoning Trace](docs/screenshots/ai_reasoning.png) | ![Heatmap View](docs/screenshots/heatmap_view.png) |
| *Real-time 3-Agent monitoring.* | *Glass-Box Strategic Analysis.* | *Venue-specific mapping.* |

---

## 🔥 Key Features

-   **Geospatial Heatmapping**: Dynamic rendering of venue-specific seating layouts (Narendra Modi Stadium, Wembley, etc.).
-   **Glass-Box AI Reasoning**: Unique **Reasoning IDs** and step-by-step traces for every Gemini-powered decision.
-   **Orchestration Playbook**: Interactive 6-phase walkthrough demonstrating the agentic feedback loop.
-   **Headless API First**: Fully exposed REST API for integration with 3rd-party stadium apps and IoT stacks.
-   **Inclusion-by-Design**: WCAG-compliant UI with Dark/Light/High Contrast modes and semantic ARIA landmarks.

---

## 🔎 AI Transparency & Strategic Logic
StadiumPulse avoids "Black-Box" decisions. We utilize **Gemini 1.5 Flash** for **Spatial Strategic Reasoning**:

*   **Observation**: Detects threshold breach (e.g., Section S1 > 90%).
*   **Analysis**: Gemini evaluates adjacency load variance to determine if a *Predictive Buffer* is safer than a *Direct Reroute*.
*   **Traceability**: Every strategic play is logged with an **Audit ID** (e.g., `GMN-7A3B2F`) and timestamp.

---

## 🔌 API Integration: Orchestration-as-a-Service
StadiumPulse acts as a central hub for external vendor systems (Turnstiles, POS, Fan Apps):

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/stadium/state` | `GET` | Retrieve real-time telemetry of all sectors. |
| `/stadium/update` | `POST` | Push sensor data from external vendor systems. |
| `/optimizer/decision` | `GET` | Audit the latest AI strategic plan and reasoning trace. |
| `/simulation/run` | `POST` | Trigger synthetic stress-test scenarios for training. |

### Reference Curl Commands
```bash
# Fetch Decisions
curl -X GET "http://localhost:8080/optimizer/decision" -H "X-API-Key: pulse-secret-default"

# Push Sensor Update
curl -X POST "http://localhost:8080/stadium/update" \
  -H "X-API-Key: pulse-secret-default" \
  -H "Content-Type: application/json" \
  -d '{"occupancy": {"S1": 9500}, "wait_times": {"G1": 2.0}}'
```

---

## 🚀 Getting Started

### 1. Environment Configuration
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PROJECT_ID=stadium-pulse-dev
STADIUM_API_KEY=pulse-secret-default
STADIUM_API_URL=http://localhost:8080
```

### 2. Installation & Pre-Flight Check
```bash
pip install -r requirements.txt
python scripts/run_tests.py     # Automated 82-test Stability Gate
```

### 3. Launching the Cluster
1.  **API Server**: `python src/api/server.py`
2.  **Visual Console**: `streamlit run src/app.py`

---

## 🧪 Testing & Reliability
*   **82 Automated Tests**: Covering security, performance, accessibility, and AI reasoning.
*   **Simulation Fallback**: Automatic shift to simulated reasoning if Gemini API connectivity is lost.
*   **CI/CD Ready**: Integrated coverage reporting (95% on core agents).

---

## ☁️ Deployment
Ready for **Google Cloud Run**.
```bash
# Deploying the Dashboard (Container binds to 8080)
gcloud run deploy stadium-pulse-ui --source . --set-env-vars GEMINI_API_KEY=$KEY --port 8080
```

---
*Built with ❤️ for the Google AI Hackathon.*
