# Brilliance — Multi‑source Research Assistant with AI Synthesis

Brilliance is a full‑stack app that gathers recent papers from multiple scholarly sources (arXiv, PubMed, OpenAlex), then produces an AI‑generated synthesis tailored to your query. It includes advanced features like domain filtering, enhanced terminology expansion, and is designed for quick local testing and simple cloud deployment.

## 🚀 Key Features

### 🔍 Enhanced Search & Terminology
Content discovery is powered by an enhanced usage of the arXiv API and other sources:
- **Terminology Expansion**: Automatically generates related terms, synonyms, and adjacent concepts (e.g., "transformer" → "self-attention", "BERT").
- **Multiple Search Strategies**: Executes multiple targeted searches with expanded terminology to find papers you might otherwise miss.
- **AI-Powered Relevance Filtering**: Uses language models to evaluate paper relevance (0.0-1.0 score) and provides reasoning, filtering out false positives.
- **Intelligent Deduplication**: Removes duplicate papers across multiple search strategies and sources.

### 🏷️ Domain Filtering System
To solve the problem of ambiguous terms (e.g., "shockwave" in Astronomy vs. Engineering), Brilliance includes a comprehensive domain context system:
- **Explicit Domain Selection**: Users can select "Include" (e.g., Engineering) and "Exclude" (e.g., Astronomy) domains.
- **Intelligent Classification**: Papers are classified into 15+ research domains (Physics, CS, Medicine, etc.) using AI and rule-based methods.
- **Context-Aware Search**: The system guides terminology expansion based on your selected domains (e.g., "catalyst" expands to "heterogeneous catalysis" in Chemistry, not social change terms).

### 🖥️ Modern Frontend
The React-based frontend is designed for transparency and control:
- **Rich Results**: Shows relevance scores (🎯 HIGHLY RELEVANT), domain tags, and synthesis.
- **Search Details**: Inspect the "black box" — see exactly what queries were generated and how many papers were filtered.
- **Quick Presets**: One-click configurations for common fields like "Engineering Focus" or "Life Sciences".

---

## 📁 Repository Structure

This project is organized for modularity and easy deployment:

### Backend (This Repo)
- **Framework**: Python Flask
- **Deployment**: Heroku (Zero Downtime Restart configured)
- **Key Components**:
    - `backend/brilliance/api/`: Flask API endpoints (`/research`, `/health`).
    - `backend/brilliance/agents/`: Research logic and orchestration.
    - `backend/brilliance/tools/`: Source fetchers (ArXiv, PubMed, OpenAlex).
    - `backend/brilliance/synthesis/`: AI synthesis logic.

### Frontend
- **Framework**: React (Create React App)
- **Deployment**: Vercel/Netlify
- **Repo**: [Brilliance Frontend](https://github.com/ECLLC42/brilliance_frontend) (Note: A copy of the frontend code is also included in `frontend/` for local development convenience).

---

## ⚡ Deployment & Zero Downtime Restart (ZDR)

The backend is configured for robust production deployment on Heroku using Gunicorn.

### ZDR Features
- **Graceful Timeouts**: Workers finish current requests before restarting (30s timeout).
- **Health Monitoring**: `/health` and `/health/detailed` endpoints.
- **Automated Checks**: `scripts/deploy-zdr.sh` script performs health checks during deployment.

### Quick Deploy to Heroku
```bash
# 1. Create App
heroku create brilliance-ws-demo

# 2. Push Code
git push heroku main

# 3. Configure Env Vars
heroku config:set FRONTEND_URL=https://your-frontend.app
heroku config:set FREE_MESSAGES_PER_IP=2
heroku config:set FREE_QUOTA_WINDOW_SECONDS=86400
heroku config:set WEB_CONCURRENCY=2

# 4. Scale
heroku ps:scale web=1
```

---

## 🛠️ Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Setup & Run
1.  **Backend Setup**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r ../requirements.txt
    ```

2.  **Frontend Setup**:
    ```bash
    cd ../frontend
    npm install
    ```

3.  **Run Both**:
    You can run them in separate terminals, or use the helper command from root:
    ```bash
    # From project root
    npx -y concurrently -k -r -n FRONTEND,BACKEND -c blue,green \
      "npm --prefix ./frontend run start" \
      "./backend/venv/bin/flask --app backend.brilliance.api.v1:app run --port 5000"
    ```

    - Frontend: `http://localhost:3000`
    - Backend: `http://localhost:5000`

### API Usage
**Endpoint**: `POST /research`
```bash
curl -X POST http://localhost:5000/research \
  -H 'Content-Type: application/json' \
  -d '{"query":"protein folding breakthroughs","max_results":3}'
```

---

## ⚙️ Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `FRONTEND_URL` | Allowed CORS origins | `*` |
| `FREE_MESSAGES_PER_IP` | Free requests before requiring key | `2` |
| `FREE_QUOTA_WINDOW_SECONDS` | Reset window for quota | `86400` (24h) |
| `REQUIRE_API_KEY` | Force API key for all requests | `0` (False) |
| `USE_ENHANCED_ARXIV` | Enable enhanced search logic | `true` |
| `ENABLE_DOMAIN_FILTERING` | Enable domain context system | `true` |

### API Keys
Users can provide their own keys via the `X-User-Api-Key` header. The backend maps this key to `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc., allowing users to bring their own model credits.

---

### License
See `LICENSE` in this repository.
