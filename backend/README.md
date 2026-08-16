# Sona Backend

Python FastAPI backend for the Sona AI music persona service.

## Run Locally

Create `backend/.env` and fill in your Spotify app credentials:

```bash
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/auth/spotify/callback
FRONTEND_URL=http://127.0.0.1:8443
```

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

If `python3 -m pip` is missing inside the virtual environment, run:

```bash
python3 -m ensurepip --upgrade
```

## API

- `GET /health`
- `GET /api/personas`
- `POST /api/recommendations`
- `GET /api/auth/spotify/status`
- `GET /api/auth/spotify/login`
- `GET /api/auth/spotify/callback`
- `GET /api/auth/spotify/me`
- `POST /api/auth/spotify/logout`
- `GET /api/spotify/devices`
- `POST /api/spotify/play`

The recommendation API currently uses mock persona and track data. Spotify OAuth,
candidate collection, and LLM persona evaluation can replace the mock service later
without changing the route shape.
