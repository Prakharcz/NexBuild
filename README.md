# 🛡️ AegisFinance: AI-Powered Personal Finance & Financial Risk Agent

<p align="center">
  <a href="https://github.com/Prakharcz/NexBuild/actions"><img src="https://github.com/Prakharcz/NexBuild/actions/workflows/ci.yml/badge.svg" alt="CI Pipeline"></a>
  <a href="https://github.com/Prakharcz/NexBuild/stargazers"><img src="https://img.shields.io/github/stars/Prakharcz/NexBuild?style=flat-square&color=emerald" alt="Stars"></a>
  <a href="https://github.com/Prakharcz/NexBuild/network/members"><img src="https://img.shields.io/github/forks/Prakharcz/NexBuild?style=flat-square" alt="Forks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-10b981.svg?style=flat-square" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat-square" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61dafb.svg?style=flat-square" alt="React 18">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ed.svg?style=flat-square" alt="Docker">
  <img src="https://img.shields.io/badge/API%20Costs-$0.00-brightgreen.svg?style=flat-square" alt="Zero Cost">
</p>

<p align="center">
  <b>A self-hosted, full-stack intelligence agent for liquidity telemetry, statistical spending anomaly detection, cash flow projections, and autonomous risk scoring.</b><br>
  <i>100% Free & Open-Source • Zero Paid APIs • Self-Contained JWT Auth • Cross-Platform</i>
</p>

---

## 📑 Table of Contents

- [✨ Core Features](#-core-features)
- [⚡ How to Run](#-how-to-run)
  - [Option 1: Instant Standalone Web App](#option-1-instant-standalone-web-app)
  - [Option 2: Docker Compose (Full Stack)](#option-2-docker-compose-full-stack)
  - [Option 3: Local Bare-Metal (Python + Node.js)](#option-3-local-bare-metal-python--nodejs)
- [🎨 Theme Color Palettes](#-theme-color-palettes)
- [📊 Sample Scenario Presets](#-sample-scenario-presets)
- [🏛️ System Architecture](#-system-architecture)
- [🧪 Automated Testing](#-automated-testing)
- [🚀 Pushing to GitHub](#-pushing-to-github)
- [🔒 Security & Privacy](#-security--privacy)
- [📄 License](#-license)

---

## ✨ Core Features

1. **Flexible Bank Statement CSV Ingestion**: Multi-format dialect parser supporting Chase, Bank of America, Wells Fargo, Citi, and custom exports.
2. **Rule-Based Categorization**: 10 financial spending categories (*Housing, Groceries, Dining, Utilities, Healthcare, Entertainment, Shopping, Income, Transportation, Uncategorized*) with inline user overrides.
3. **Recurring Charges & Silent Price Hike Detection**: Automatically detects subscription cadences (weekly, biweekly, monthly) and flags unannounced price hikes (e.g. Netflix jumping from $15.99 to $19.99).
4. **Statistical Anomaly Outlier Engine**: Identifies unusual expenses using category-specific **Interquartile Range (IQR)** and **Z-score** ($|z| \ge 2.5\sigma$) outlier detection.
5. **Cash Flow & Moving Average Balance Forecast**: Projects 30 to 60-day daily balance curves with scheduled recurring commitments and $\pm 1.96 \sigma \sqrt{t}$ confidence bounds.
6. **Financial Risk Score (0–100)**: Evaluates months of liquidity buffer, spending volatility ($CV = \frac{\sigma}{\mu}$), and savings margin into an interactive semi-circle risk gauge.
7. **Savings Goals Tracker**: Create, track, and fund savings milestones with real-time percentage progress bars and quick contribution actions.
8. **AI Recommendations with Fallback**: Generates actionable financial advice using a local Ollama model if installed, with an automatic, graceful fallback to deterministic explanations.
9. **Human-in-the-Loop Approvals & Audit Trail**: AI recommendations require explicit user confirmation (*APPROVED, REJECTED, ACTED_ON*) and are permanently logged to an immutable audit ledger.

---

## ⚡ How to Run

### Option 1: Instant Standalone Web App
No server, Python, or Node.js required. Open the standalone app directly in any browser:

- **Windows**: Double-click [`run_app.bat`](run_app.bat) or open [`index.html`](index.html).
- **macOS / Linux**: Run `./run_app.sh` or open `index.html`.

---

### Option 2: Docker Compose (Full Stack)
Spins up FastAPI, PostgreSQL 16, Redis 7, React Nginx SPA, and local Ollama inference bridge in isolated containers:

```bash
# 1. Clone repository
git clone https://github.com/Prakharcz/NexBuild.git
cd NexBuild

# 2. Setup environment variables
cp .env.example .env

# 3. Build & start containers
docker-compose up --build
