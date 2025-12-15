#!/bin/bash

# Start backend in background
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$DIR/.."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r ../requirements.txt
# Load environment variables and start Flask
python3 -c "
from dotenv import load_dotenv
load_dotenv('../.env')
from brilliance.api.v1 import app
app.run(host='0.0.0.0', port=8000, debug=False)
" &

# Start frontend
cd ../frontend
npm install
npm start
