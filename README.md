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
  <i>100% Free & Open-Source • Zero Paid APIs • Self-Contained JWT Auth • Runs on Any Machine</i>
</p>

---

## 📑 Table of Contents

- [🎮 Live Interactive Demo](#-live-interactive-demo)
- [✨ Key Features](#-key-features)
- [🎨 Theme Color Palettes](#-theme-color-palettes)
- [📊 4 Built-In Scenario Presets](#-4-built-in-scenario-presets)
- [⚡ 3 Ways to Run (Any System)](#-3-ways-to-run-any-system)
  - [Option 1: Instant Zero-Install Web App](#option-1-instant-zero-install-web-app-recommended)
  - [Option 2: Docker Compose Full Stack](#option-2-docker-compose-full-stack)
  - [Option 3: Local Bare-Metal (Python + Node.js)](#option-3-local-bare-metal-python--nodejs)
- [🏛️ System Architecture](#-system-architecture)
- [🧪 Automated Testing](#-automated-testing)
- [🚀 Pushing to GitHub (Bypass 100-File Limit)](#-pushing-to-github-bypass-100-file-limit)
- [🔒 Security & Privacy](#-security--privacy)
- [📄 License](#-license)

---

## 🎮 Live Interactive Demo

> **No installation needed!** Run AegisFinance in under 2 seconds:

| Platform | How to Launch | Action |
| :--- | :--- | :--- |
| **Online Web (GitHub Pages)** | Runs directly from GitHub | [👉 Launch Live Web App](https://prakharcz.github.io/NexBuild/) |
| **Windows** | Double-click `run_app.bat` or `index.html` | Opens in Default Browser |
| **macOS / Linux** | Run `./run_app.sh` or open `index.html` | Opens in Default Browser |

---

## ✨ Key Features

<details open>
<summary><b>🔍 1. Flexible CSV Statement Ingestion & Categorization</b></summary>
<br>

- Multi-format dialect detection supporting **Chase, Bank of America, Wells Fargo, Citi, Apple Card**, and custom spreadsheets.
- Rule-based keyword matching across **10 spending categories** (*Housing, Groceries, Dining, Utilities, Healthcare, Entertainment, Shopping, Income, Transportation, Uncategorized*).
- Inline category re-assignment with instant database sync.

</details>

<details>
<summary><b>🔁 2. Recurring Charge & Price Hike Detection</b></summary>
<br>

- Cadence interval grouping algorithm detecting weekly, biweekly, and monthly recurring charges.
- **Silent Price Hike Sentry**: Flags when subscription costs creep up (e.g., Netflix jumping from $15.99 to $19.99, Gym rates rising $45 &rarr; $59).
- Surfaces reclaimable subscription cash with 1-click action recommendations.

</details>

<details>
<summary><b>🚨 3. Statistical Anomaly & Outlier Engine (IQR + Z-Score)</b></summary>
<br>

- Category-segmented **Interquartile Range (IQR)**: flags charges exceeding $Q_3 + 1.5 \times \text{IQR}$.
- **Z-Score Calculation**: flags extreme statistical spikes where $|z| \ge 2.5\sigma$.
- Excludes income deposits to prevent positive paychecks from triggering expense alerts.

</details>

<details>
<summary><b>📈 4. Cash Flow & Moving Average Balance Forecaster</b></summary>
<br>

- 30 to 60-day predictive moving-average daily balance projections.
- Injects known scheduled recurring paychecks and bills into future timeline.
- Dynamically calculates upper and lower **95% confidence intervals** ($\pm 1.96 \sigma \sqrt{t}$).

</details>

<details>
<summary><b>🛡️ 5. Financial Risk Score Engine (0–100)</b></summary>
<br>

- Composite scoring evaluating:
  - **Liquidity Runway Buffer**: Months of essential obligations covered by current reserves.
  - **Spending Volatility**: Coefficient of variation ($CV = \frac{\sigma}{\mu}$).
  - **Net Savings Margin**: Percentage of net income preserved monthly.
- Renders an interactive SVG gauge with real-time risk grading (*Low Risk*, *Moderate Risk*, *High Risk Alert*).

</details>

<details>
<summary><b>🎯 6. Savings Goals & Runway Milestones</b></summary>
<br>

- Interactive goal builder with category milestones (*Emergency Buffer, Home Down Payment, Travel, Vehicle, Wealth*).
- Dynamic funding bars, remaining balance computation, and quick contribution buttons (`+$50`, `+$100`).
- Full persistent CRUD saved directly to `localStorage` or PostgreSQL.

</details>

<details>
<summary><b>⚖️ 7. Human-in-the-Loop Decision Approvals & Immutable Audit Log</b></summary>
<br>

- AI recommendations are strictly advisory — actions require **explicit user confirmation** via modal approval.
- Every decision (*APPROVED, REJECTED, ACTED_ON*) is cryptographically timestamped and stored in an immutable audit ledger.

</details>

---

## 🎨 Theme Color Palettes

Customize the UI to match your aesthetic with the integrated **Palette Selector** in the top navigation bar:

| Swatch | Palette Name | Primary Hex | Highlight Role |
| :---: | :--- | :---: | :--- |
| 🌿 | **Emerald Green** *(Default)* | `#10b981` | Classic fintech, growth, prosperity |
| 🔷 | **Sapphire Blue** | `#2563eb` | Corporate neobanking & institutional trust |
| 🔮 | **Electric Violet** | `#8b5cf6` | High-tech AI agent aesthetic |
| 🌅 | **Sunset Amber** | `#f59e0b` | High contrast & energetic gold |
| 🌹 | **Ruby Rose** | `#f43f5e` | Bold crimson & premium ruby |
| 🌊 | **Cyber Teal** | `#06b6d4` | Clean Scandinavian cyan tone |
| 🍇 | **Deep Indigo** | `#6366f1` | Modern developer SaaS midnight tone |
| 🪙 | **Obsidian Slate** | `#475569` | Executive minimalist monochrome |
| 🎨 | **Custom Hex Picker** | *User Defined* | Pick ANY color from native OS color wheel |

> *Theme palettes instantly re-color active navigation tabs, buttons, gradient badges, Risk Gauge meters, and Chart.js forecast strokes. Preferences persist in `localStorage` across visits.*

---

## 📊 4 Built-In Scenario Presets

Easily test and preview all platform capabilities using the **Scenario Selector** dropdown in the top navbar or via the Upload view:

| Scenario Preset | Financial Focus | Profile Highlights |
| :--- | :--- | :--- |
| **1. Stable Saver** | Low Risk & Forecasting | • 58% savings rate, 8.5 months runway, steady wealth growth.<br>• **Score: 92/100 (Low Risk)**. |
| **2. Subscription Creep** | Cadence & Price Hikes | • 8 recurring services detected.<br>• Price hikes: Netflix (+25%), Gym (+31%), NYTimes (+525%).<br>• Identifies **$188/mo** in reclaimable cash. |
| **3. Volatile Outliers** | IQR & Z-Score Anomalies | • Auto-flags extreme charges: $2,450 Dental, $1,850 Auto repair, $1,120 Splurge.<br>• Triggers volatility warnings. |
| **4. Liquidity Crunch** | High-Risk Alert & Action | • 0.4 months runway, high food delivery burn rate.<br>• Predicts overdraft in 22 days.<br>• **Score: 32/100 (High Risk Alert)**. |

---

## ⚡ 3 Ways to Run (Any System)

### Option 1: Instant Zero-Install Web App (Recommended)

Run the complete web application with zero dependencies (no Docker, Node, or Python needed):

```bash
# Clone the repository
git clone https://github.com/Prakharcz/NexBuild.git
cd NexBuild

# Windows:
run_app.bat

# macOS / Linux:
chmod +x run_app.sh && ./run_app.sh
