# Distributed Chatbot System

This project is an Ollama-powered chatbot that supports both local usage and a distributed cloud-local architecture.

## 🚀 Distributed Architecture (Cloud + Local)
This architecture allows you to run the heavy processing on your local machine while accessing the UI from anywhere via Streamlit Cloud.

**Architecture:**
`User → Streamlit Cloud → ngrok Tunnel → Local PC (FastAPI) → Processing`

**Step-by-Step Setup:**
See [MIGRATION_GUIDE.md](file:///c:/Users/IT%20Common/Desktop/Chatbot/MIGRATION_GUIDE.md) for detailed instructions on setting up Distributed mode.

---

## 💻 Local Setup
1. **Clone the Repo**.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Set `API_MODE=local`.
4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

---

## 🔌 API Documentation
The system exposes a FastAPI backend for external integrations.

### Prerequisites
- Ollama running locally with `qwen2.5vl:7b` model.

### Running the API
Double-click `run_api.bat` OR run:
```bash
python api.py
```
Server starts at `http://0.0.0.0:8000`.

### Endpoints
- `GET /health`: Connectivity check.
- `POST /chat`: Main chat endpoint.

**[👉 Click here for Detailed API Usage & Examples](API_USAGE_GUIDE.md)**

---

## 🛠 Features
- **PDF & Image Support**: Process documents and images directly in the chat.
- **Hybrid Mode**: Toggle between local processing and remote API interaction.
- **Health Monitoring**: Real-time status indicator for API connectivity.
- **Secure Tunneling**: Easy integration with ngrok for public access.
