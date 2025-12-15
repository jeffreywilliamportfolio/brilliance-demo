#!/bin/bash

# Deploy ZDR Script
# This script is a placeholder for your deployment logic.
# It should trigger a deployment (e.g., git push heroku main) and then monitor health.

APP_NAME="brilliance-ws-demo" # Change this to your app name

echo "🚀 Deploying to $APP_NAME..."
# git push heroku main

echo "🔍 Starting Monitor..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 "$DIR/monitor-zdr.py" "https://$APP_NAME.herokuapp.com"
