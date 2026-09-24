# CALIP Platform - Production Deployment Guide

This guide details how to deploy the CALIP Legal Case & Document Intelligence Platform to **Vercel**, **Render**, **Railway**, and **Docker**.

---

## 1. Deploying to Vercel (Serverless)

### Architecture on Vercel
CALIP is configured for Vercel using the official `@vercel/python` builder via [vercel.json](file:///c:/Users/impra/Desktop/CALIP/vercel.json) and [api/index.py](file:///c:/Users/impra/Desktop/CALIP/api/index.py).

### Prerequisites & Considerations
- **Serverless Execution Model**: Vercel executes requests inside transient AWS Lambda functions.
- **Read-Only Filesystem**: Vercel allows writing only to `/tmp` (CALIP automatically copies SQLite to `/tmp/calip.db` on cold boot if SQLite is used, or connects to external PostgreSQL).
- **Function Execution Timeout**:
  - Hobby (Free) plan: **10-15 seconds** per request.
  - Pro plan: **up to 60-300 seconds**.
  *(Note: Because LLM reasoning with NVIDIA NIM can take 5–10s, Vercel Pro is recommended for high-volume legal summaries, or Render/Railway for unrestricted execution).*
- **Background Daemon Worker**: Background threads (`auto_sync`) are automatically disabled on Vercel to conform to serverless lifecycle rules.

### Step-by-Step Vercel Deployment

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "feat: configure CALIP for Vercel and container production"
   git push origin main
   ```

2. **Import into Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/new).
   - Select your GitHub repository (`CALIP`).
   - Framework Preset: **Other**.
   - Root Directory: `./` (leave default).

3. **Configure Environment Variables in Vercel Settings**:
   Add the following environment variables:
   | Variable | Value / Description |
   | :--- | :--- |
   | `LLM_PROVIDER` | `nvidia` (or `groq` / `gemini`) |
   | `NVIDIA_API_KEY` | `your_nvidia_api_key_here` (from build.nvidia.com) |
   | `NVIDIA_MODEL` | `mistralai/mistral-nemotron` |
   | `GROQ_API_KEY` | `your_groq_api_key_here` (from console.groq.com) |
   | `GEMINI_API_KEY` | `your_gemini_api_key_here` (from aistudio.google.com) |
   | `APP_ENV` | `production` |
   | `SERVERLESS` | `true` |
   | `DATABASE_URL` | *(Optional)* If using external PostgreSQL (Supabase / Neon), set `postgresql://user:pass@host:5432/db` |

4. **Click Deploy**:
   Vercel will install dependencies from [requirements.txt](file:///c:/Users/impra/Desktop/CALIP/requirements.txt) and publish your platform to `https://<your-project>.vercel.app`.

---

## 2. Deploying to Render.com (Recommended for Full Python/FastAPI)

Render provides persistent containers, supports background workers (`auto_sync`), has no 10-second serverless timeout, and offers a free tier.

### Render Steps:
1. Connect your GitHub repository to [Render Dashboard](https://dashboard.render.com/).
2. Select **New Web Service**.
3. Choose **Docker** environment (or Python 3.11).
4. Set Build & Start Command:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `LLM_PROVIDER`: `nvidia`
   - `NVIDIA_API_KEY`: your key
   - `NVIDIA_MODEL`: `mistralai/mistral-nemotron`
   - `GROQ_API_KEY`: your key
   - `AUTO_SYNC_ENABLED`: `true`

---

## 3. Deploying with Docker / Docker Compose

For a VPS, AWS EC2, or DigitalOcean Droplet:

```bash
# Build and run container in detached mode
docker compose up -d --build

# View real-time logs
docker compose logs -f

# Verify service health
curl http://localhost:8000/health
```

---

## 4. Verification Checklist Post-Deployment

- [ ] Open `https://<your-domain>/` and verify homepage loads legal cases.
- [ ] Open `https://<your-domain>/health` - verify JSON response `{ "status": "healthy" }`.
- [ ] Open `https://<your-domain>/documents` - verify documents list.
- [ ] Open `https://<your-domain>/documents/doc-Documents_1768563645_pdf` - verify AI Executive Brief powered by NVIDIA NIM renders with full legal tabs.
- [ ] Test RAG Ask endpoint: `https://<your-domain>/api/rag/ask?query=What+cases+are+recorded%3F`
