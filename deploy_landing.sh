#!/bin/bash
# Deploy landing page + app.py changes to VPS
# Run: bash deploy_landing.sh

VPS="ubuntu@43.134.97.56"
REMOTE="/home/ubuntu/triage_new"
LOCAL="/Users/macintosh/Documents/triage_new"

echo "=== Deploying landing page update ==="

scp "$LOCAL/pages/landing_page.py"  "$VPS:$REMOTE/pages/landing_page.py"  && echo "✓ landing_page.py"
scp "$LOCAL/app.py"                  "$VPS:$REMOTE/app.py"                  && echo "✓ app.py"

echo "=== Restarting service ==="
ssh "$VPS" "sudo systemctl restart triage_new && sleep 2 && sudo systemctl status triage_new --no-pager | head -15"

echo "=== Done — open http://43.134.97.56:8080/ ==="
