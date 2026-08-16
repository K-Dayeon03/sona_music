# sona_music
AI 페르소나 취향 큐레이션

## 프로젝트 구조

- `frontend/` - React/Vite 프론트엔드
- `backend/` - Python FastAPI 백엔드
- `doc/` - 요구사항과 아키텍처 문서

## 실행

### 백엔드

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm run dev
```

## 문서

- [서비스 요구사항](doc/REQUIREMENTS.md)
- [디자인 요구사항](doc/DESIGN_REQUIREMENTS.md)
- [추천 아키텍처](doc/ARCHITECTURE.md)
- [AI 소셜 요구사항](doc/AI_SOCIAL_REQUIREMENTS.md)
