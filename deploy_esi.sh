#!/bin/bash
# Deploy ESI triage files to VPS
# Run: bash deploy_esi.sh

VPS="ubuntu@43.134.97.56"
REMOTE="/home/ubuntu/triage_new"
LOCAL="/Users/macintosh/Documents/triage_new"

echo "=== Deploying ESI triage update ==="

scp "$LOCAL/pages/step4_abcde.py" "$VPS:$REMOTE/pages/step4_abcde.py" && echo "✓ step4_abcde.py"
scp "$LOCAL/utils/triage_engine.py" "$VPS:$REMOTE/utils/triage_engine.py" && echo "✓ triage_engine.py"
scp "$LOCAL/pages/step5_triage.py" "$VPS:$REMOTE/pages/step5_triage.py" && echo "✓ step5_triage.py"

echo "=== Restarting service ==="
ssh "$VPS" "sudo systemctl restart triage_new && sleep 2 && sudo systemctl status triage_new --no-pager | head -20"

echo "=== Done ==="
