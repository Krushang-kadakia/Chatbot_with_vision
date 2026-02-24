# Migration Guide: Distributed Architecture

This guide explains how to transition from a local-only setup to a distributed architecture using Streamlit Cloud and ngrok.

## Architecture Overview
`User → Streamlit Cloud → ngrok Tunnel → Local PC (FastAPI) → Ollama/Processing`

## Phase 1: Local Backend Setup
1.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment**:
    - Copy `.env.example` to `.env`.
    - Set `API_MODE=local` for initial testing.
3.  **Run the API**:
    ```bash
    python api.py
    ```
    Verify it's running at `http://localhost:8000`.

## Phase 2: Expose via ngrok
1.  **Start ngrok**:
    ```bash
    ngrok http 8000
    ```
    (Best practice: Use a fixed domain if you have a Pro/Static domain).
2.  **Note the URL**: e.g., `https://xyz-123.ngrok-free.app`.

## Phase 3: Streamlit Cloud Deployment
1.  **Push to GitHub**: Ensure your repository is up to date.
2.  **Deploy to Streamlit Cloud**:
    - Connect your repo.
    - **Crucial**: Go to **Settings > Secrets** and add:
      ```toml
      API_MODE = "remote"
      API_URL = "https://your-ngrok-url.ngrok-free.app"
      MODEL_NAME = "qwen2.5vl:7b"
      ```
3.  **Launch**: Your app should now connect to your local PC.

## Configuration Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `API_MODE` | `local` (uses imports) or `remote` (uses API) | `local` |
| `API_URL` | Base URL of the FastAPI backend | `http://localhost:8000` |
| `MODEL_NAME` | Ollama model to use | `qwen2.5vl:7b` |

## Troubleshooting
- **API Offline**: Ensure `api.py` is running and ngrok is active.
- **Timeout**: Large PDFs may take longer than 120s. Check local logs for progress.
- **Port 8000 Busy**: Change port in `api.py` and ngrok command.
