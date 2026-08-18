# Sona 무료 실험 배포 가이드

Sona MVP는 사용자 로그인과 Spotify OAuth Redirect 흐름이 없으므로, 프론트엔드와 백엔드를 무료 티어에 나눠 올리기 쉽다. 다만 실제 곡 검색을 위해 백엔드에는 Spotify 앱의 Client Credentials가 필요하다.

## 권장 조합

- Backend: Render Free Web Service
- Frontend: Vercel, Netlify, 또는 Cloudflare Pages

## Backend on Render

루트의 `render.yaml`을 사용한다.

```yaml
services:
  - type: web
    name: sona-music-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    plan: free
```

배포 후 다음 API가 열리면 성공이다.

```text
https://<render-app>.onrender.com/health
https://<render-app>.onrender.com/api/feed
https://<render-app>.onrender.com/api/collabs
```

Render 무료 서버는 비활성 상태가 길어지면 잠들 수 있다. 실험용으로는 괜찮지만 첫 요청이 느릴 수 있다.

Render 환경변수에는 다음 값을 추가한다. 로컬의 `backend/.env` 파일은 Render 서버로 자동 업로드되지 않으므로, 배포 환경에서는 Render 대시보드에 같은 값을 직접 등록해야 한다.

```text
SPOTIFY_CLIENT_ID=<Spotify Dashboard 앱 Client ID>
SPOTIFY_CLIENT_SECRET=<Spotify Dashboard 앱 Client Secret>
SPOTIFY_MARKET=US
```

사용자 로그인을 하지 않으므로 Spotify Redirect URI는 설정하지 않아도 된다.

## Frontend

프론트엔드 배포 서비스에서 다음 환경변수를 설정한다.

```text
VITE_API_BASE_URL=https://<render-app>.onrender.com
```

빌드 설정:

```text
Root directory: frontend
Build command: npm run build
Output directory: dist
```

로컬 개발에서는 `VITE_API_BASE_URL`을 비워둔다. Vite dev server가 `/api` 요청을 로컬 백엔드 `http://127.0.0.1:8000`으로 프록시한다.

## MVP에서 필요 없는 것

- OAuth Redirect URI
- 사용자 로그인
- 데이터베이스 계정

SQLite 파일은 백엔드 실행 중 자동 생성된다. 무료 호스팅에서 파일 시스템이 재시작 때 초기화될 수 있으므로, MVP에서는 피드가 Spotify 검색 결과로 다시 생성되어도 괜찮다는 전제로 사용한다.
