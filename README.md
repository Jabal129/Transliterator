# Transliterator 🌍

A web application that converts text from various languages (Spanish, Chinese, Japanese, Korean, Vietnamese) to Arabic transliteration using FastAPI backend and React frontend.

## Local Development

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm

### Setup

1. **Install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Build the React app (optional, for testing production build):**
   ```bash
   npm run build
   ```

### Running Locally

**Terminal 1 - Frontend (React + Vite):**
```bash
npm run dev
```
Access at: http://localhost:5173

**Terminal 2 - Backend (FastAPI + Uvicorn):**
```bash
cd backend
python -m uvicorn main:app --reload
```
API available at: http://localhost:8000

## Deployment to Railway.app

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Quick Deploy
1. Push to GitHub
2. Sign up at https://railway.app
3. Connect your GitHub repo
4. Set `ALLOWED_ORIGINS` environment variable
5. Done! Your app is live.

## Project Structure

```
.
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── services/           # API service layer
│   └── styles/             # CSS styles
├── backend/                # FastAPI backend
│   ├── Aljamiado.py        # Spanish → Arabic
│   ├── Xiaoerjing.py       # Chinese → Arabic
│   ├── Araboji.py          # Japanese → Arabic
│   ├── Soagyeong.py        # Korean → Arabic
│   ├── Tieunhikinh.py      # Vietnamese → Arabic
│   └── main.py             # FastAPI app
├── public/                 # Static assets
└── Dockerfile              # Docker configuration for deployment
```

## Supported Languages

- **Spanish** (Aljamiado) - Spanish text → Arabic script
- **Chinese** (Xiaoerjing) - Chinese text → Arabic romanization with tones
- **Japanese** (Araboji) - Japanese text → Arabic script
- **Korean** (Soagyeong) - Korean text → Arabic script  
- **Vietnamese** (Tiếng Hát) - Vietnamese text → Arabic script

## API Endpoints

### Production/Deployed
- `POST /api/transliterate` - Transliterate text
- `GET /api/health` - Health check

### Local Development
- `POST /transliterate` - Transliterate text
- `GET /health` - Health check

## License
MIT

