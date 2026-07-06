<div align="center">

<h1>SafeCorridor</h1>

<p>
<b>Passive Ride Monitoring • Deterministic Risk Assessment • Explainable Safety Escalation</b>
</p>

<p>
Real-time telemetry, deterministic risk scoring, and transparent safety state transitions.
</p>

<p>
<a href="./LOCAL_SETUP.md">
<img src="https://img.shields.io/badge/Setup-Guide-2563EB?style=for-the-badge">
</a>
<a href="./android-app/SafeCorridorTracker/Apk/app-debug.apk">
<img src="https://img.shields.io/badge/Android-APK-16A34A?style=for-the-badge">
</a>
</p>

<p>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black">
<img src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white">
<img src="https://img.shields.io/badge/Kotlin-7F52FF?style=flat-square&logo=kotlin&logoColor=white">
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white">
<img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square">
</p>

<p align="center">
<a href="#problem">Problem</a> •
<a href="#why-safecorridor">Why SafeCorridor?</a> •
<a href="#key-capabilities">Features</a> •
<a href="#architecture">Architecture</a> •
<a href="#performance">Performance</a> •
<a href="#api-overview">API</a> •
<a href="#installation--running">Installation</a> •
<a href="#project-status--roadmap">Roadmap</a> •
<a href="#contributing">Contributing</a>
</p>

<br>

<table align="center">
<tr>
<td align="center">
<b>Language</b><br>
Kotlin + Python
</td>
<td align="center">
<b>Architecture</b><br>
Client → API → Risk Engine
</td>
<td align="center">
<b>Communication</b><br>
REST + WebSocket
</td>
<td align="center">
<b>Platform</b><br>
Android
</td>
<td align="center">
<b>License</b><br>
MIT
</td>
</tr>
</table>

</div>

---

## At a Glance

<br>

<table align="center">
<tr>
<td align="center">
📱<br>
<b>Start Ride</b>
</td>
<td align="center">
📍<br>
<b>Collect GPS</b>
</td>
<td align="center">
🧠<br>
<b>Analyze Behaviour</b>
</td>
<td align="center">
⚠️<br>
<b>Accumulate Risk</b>
</td>
<td align="center">
📊<br>
<b>Update Dashboard</b>
</td>
<td align="center">
🏁<br>
<b>End Ride</b>
</td>
</tr>
</table>

<br>

## Problem

Modern ride-monitoring systems often rely on proprietary black-box algorithms or community-driven reporting, leaving passengers vulnerable when active communication is impossible. Erratic driving behavior, unprompted prolonged stops, and significant deviations from expected routes are strong early indicators of compromised safety, but these metrics are rarely analyzed collectively in real-time to escalate safety states transparently.

## Why SafeCorridor?

| Conventional Systems | SafeCorridor |
| :--- | :--- |
| Black-box decisions | Deterministic evaluation |
| Binary alerts | Progressive risk accumulation |
| Minimal transparency | Explainable decision logs |
| Static thresholds | Behavior over time |
| Manual interpretation | Visual risk timeline |

## Key Capabilities

| Capability | Status |
| :--- | :--- |
| Passive Monitoring | ✅ |
| Route Corridor Analysis | ✅ |
| Risk Accumulation | ✅ |
| Explainability Logs | ✅ |
| Real-time Dashboard | ✅ |
| Offline Buffering | 🚧 |
| Authentication | 🚧 |

## Design Principles

- **Deterministic over probabilistic:** The current implementation prioritizes deterministic mathematical models and explainable rules over opaque predictive models.
- **Explainability before automation:** Every alert must have a traceable, logged reason.
- **Privacy by default:** Data is strictly session-scoped.
- **No long-term profiling:** No driver habits or historical paths are analyzed.
- **Observable system behavior:** The dashboard reflects exactly what the backend sees.
- **Progressive risk accumulation:** Risk builds incrementally based on sustained evidence.

## Architecture

```text
Android App
      │
      ▼
 REST API (FastAPI)
      │
      ▼
Session Manager
      │
      ▼
Risk Engine
      │
      ▼
State Machine
      │
      ├─────────────► SQLite
      │
      ▼
WebSocket Manager
      │
      ▼
React Dashboard
```

### Data Flow
`GPS` ➔ `Android Foreground Service` ➔ `REST API` ➔ `Validation` ➔ `Risk Engine` ➔ `State Machine` ➔ `SQLite` ➔ `WebSocket` ➔ `Dashboard`

## Explainability

A core tenet of SafeCorridor is that the dashboard should never output a generalized "Danger" warning without evidence. Every point of risk is strictly traceable to an observable ride behavior.

```text
13:42:12  Minor route deviation (+0.8)
13:42:17  Elevated speed (+1.1)
13:42:23  Moving away from destination (+1.4)
13:42:28  Unexpected stop (+1.6)

Risk = 46
State = MONITORING
```

## API Overview

### POST `/ride/start`
Initializes a new ride session.
- **Request:**
  ```json
  { "startLocation": { "lat": 21.14, "lon": 79.08 }, "endLocation": { "lat": 21.16, "lon": 79.09 } }
  ```
- **Response:**
  ```json
  { "sessionId": "1783375333839" }
  ```

### POST `/ride/telemetry`
Ingests high-frequency GPS telemetry.
- **Request:**
  ```json
  { "sessionId": "1783375333839", "location": { "lat": 21.15, "lon": 79.085 }, "speed": 15, "accuracy": 8 }
  ```
- **Response:**
  ```json
  { "riskScore": 4.5, "severity": "NORMAL", "reasons": [] }
  ```

### POST `/ride/end`
Finalizes and archives the active session.
- **Request:**
  ```json
  { "sessionId": "1783375333839" }
  ```
- **Response:**
  ```json
  { "status": "ended" }
  ```

### GET `/health`
Health check to verify backend operational status.
- **Response:**
  ```json
  { "status": "healthy" }
  ```

## Configuration Parameters

The system relies on hard mathematical constants configurable within `backend/risk_engine.py`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `MAJOR_CORRIDOR_M` | `100.0` | Maximum tolerated cross-track distance before a persistent deviation is recorded. |
| `MINOR_CORRIDOR_M` | `20.0` | Threshold for detecting minor early-warning deviations. |
| `MAX_SPEED_MPS` | `30.0` | Upper threshold for unsafe speed (108 km/h). |
| `ELEVATED_SPEED_MPS` | `20.0` | Threshold for tracking aggressive or increasing speed (72 km/h). |
| `DECAY_RATE` | `0.5` | Points deducted per second when behavior returns to normal parameters. |

## Performance

SafeCorridor is engineered for high-throughput, low-latency telemetry ingestion:

- **Telemetry interval:** 5 seconds
- **Average latency:** <100 ms
- **Memory:** ~30 MB footprint
- **Database:** SQLite WAL (Write-Ahead Logging)
- **Risk evaluation:** O(1) time complexity
- **Location accuracy:** 6–12 m typical

## Project Structure

```text
safecorridor/
├── android-app/          # Foreground telemetry collection
│   ├── app/src/main/     
│   └── build.gradle.kts
├── backend/              # REST API, risk evaluation, state management, persistence
│   ├── main.py           
│   ├── risk_engine.py    
│   ├── session_manager.py
│   └── database.py       
├── dashboard/            # Real-time monitoring interface
│   ├── src/              
│   ├── public/
│   └── package.json
└── LOCAL_SETUP.md        # Comprehensive local setup guide
```

## Installation & Running

For a comprehensive step-by-step guide on running the emulator and dashboard together, see [LOCAL_SETUP.md](./LOCAL_SETUP.md).

**Requirements:**
- Python 3.10+
- Node.js 18+
- Android Studio Iguana+
- Git

**Quick Start Backend:**
```bash
git clone https://github.com/ShadyNights/Safe-Corridor.git
cd Safe-Corridor/backend
pip install -r requirements.txt
python main.py
```

**Quick Start Dashboard:**
```bash
cd ../dashboard
npm install
npm run dev
```

## Project Status & Roadmap

- [x] Android telemetry
- [x] Dashboard
- [x] Risk engine
- [x] Explainability engine
- [x] Session management
- [ ] Offline buffering
- [ ] PostgreSQL
- [ ] Authentication
- [ ] CI/CD

## Current Limitations

- No external emergency integration (e.g., 911 dispatch).
- Single-device ride monitoring only.
- Relies on local SQLite storage.
- No user authentication layer.
- Offline buffering is still under development.

*These limitations are intentional design boundaries rather than system failures.*

## Testing & Security

**Testing:**
Automated unit and integration tests are planned as part of the project's next engineering milestone.

**Security:**
- Session isolation is enforced.
- Input validation via Pydantic.
- HTTPS enforcement (Planned).
- Authentication (Planned).
- Device authentication (Planned).

## Contributing

Contributions are welcome. Please ensure that PRs strictly adhere to the project's deterministic and privacy-first engineering philosophies. 

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/OfflineBuffering`).
3. Ensure no random generators (`Math.random()`, `random.choice`) are used for core telemetry or state logic.
4. Commit your changes (`git commit -m 'feat: add offline buffering to TrackerService'`).
5. Push to the branch (`git push origin feature/OfflineBuffering`).
6. Open a Pull Request.

## Author

**Kashif Ansari**
- GitHub: [@ShadyNights](https://github.com/ShadyNights)
- LinkedIn: [kashifansari18](https://www.linkedin.com/in/kashifansari18)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

<hr>

<div align="center">

<b>SafeCorridor</b>

<br><br>

Deterministic Engineering • Explainable Decision Making • Privacy by Design

<br><br>

Made with Python, FastAPI, React, Kotlin, and SQLite.

</div>
