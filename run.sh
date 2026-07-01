#!/usr/bin/env bash
# HireIQ V1 — run the full pipeline, then launch the dashboard.
# Usage: bash run.sh
set -euo pipefail

# Resolve the project root (directory of this script).
cd "$(dirname "$0")"

echo "[HireIQ V1] Running pipeline..."
python -m src.pipeline

echo "[HireIQ V1] Launching dashboard..."
streamlit run app.py
