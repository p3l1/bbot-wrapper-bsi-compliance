#!/bin/bash
source targets.env

# Create local python environment
python3 -m venv report/.venv
source report/.venv/bin/activate
pip install -r report/requirements.txt

echo "Generating report..."
python3 report/generate_report.py -p -j scans/$BBOT_SCAN_NAME/output.ndjson
echo "Opening PDF report..."
open report/output/report.pdf
