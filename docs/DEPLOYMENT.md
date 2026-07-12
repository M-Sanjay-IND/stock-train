# Deployment Guide

## Frontend — Vercel

1. Push code to GitHub

2. Connect repository to [Vercel](https://vercel.com)

3. Set:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.onrender.com`

5. Deploy

---

## Backend — Render

1. Push code to GitHub

2. Create new **Web Service** on [Render](https://render.com)

3. Set:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app --bind 0.0.0.0:$PORT`

4. Add environment variables:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = (generate a strong secret)
   - `DATABASE_URL` = (your PostgreSQL URL if using, or leave for SQLite)

5. Deploy

---

## Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Backend: http://localhost:5000
Frontend: http://localhost:5173 (proxied to backend)
