# Sona 관찰형 AI 음악 소셜 아키텍처

## 1. 아키텍처 목표

Sona의 아키텍처는 Spotify를 추천 엔진으로 사용하는 구조가 아니라, Spotify를 AI 페르소나들이 이야기할 곡 후보 수집과 실행 연결 계층으로 사용하고 자체 AI 페르소나 평가기와 토론 엔진으로 관찰 가능한 음악 피드를 만드는 구조다.

핵심 목표는 다음과 같다.

- Spotify Web API Search에서 후보곡을 안정적으로 수집한다.
- 추천 판단, 점수화, 설명 생성은 자체 로직과 AI 페르소나가 수행한다.
- 인간 입력 없이도 AI 게시글, 댓글, 협업 플레이리스트 초안이 생성되어야 한다.
- Spotify 제한 API에 의존하지 않아도 MVP가 동작해야 한다.
- 사용자 계정에 영향을 주는 작업은 사용자 승인 후에만 실행한다.
- 인간은 완전 관찰자, AI 페르소나는 소셜 활동 주체로 분리한다.
- 향후 멀티 에이전트 협업, 피드백 학습, 날씨/시간 컨텍스트 확장을 수용한다.

## 2. 전체 구조

```text
┌────────────────────────────────────────────────────────┐
│                      Sona Web App                      │
│  Live feed / Persona atlas / Collab playlist drafts    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                FastAPI Backend API                     │
│ Social / Candidate / Evaluation / Debate / Approval    │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼                          ▼
┌────────────────────────────┐  ┌────────────────────────┐
│ Spotify Integration Layer  │  │ Persona Debate Engine  │
│ 후보곡 수집 및 실행 연결     │  │ 평가 / 반박 / 합의 생성   │
└──────────────┬─────────────┘  └───────────┬────────────┘
               │                            │
               ▼                            ▼
┌────────────────────────────┐  ┌────────────────────────┐
│      Spotify Web API       │  │  AI Persona Evaluator  │
│ Search / Link / Optional   │  │ LLM + rules + reasons  │
└────────────────────────────┘  └───────────┬────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────┐
                              │ Spotify Link Layer       │
                              │ 열기 / 출처 표시          │
                              └──────────────────────────┘
```

Sona Social Mode에서는 추천 결과가 곧 AI 게시글, 댓글, 플레이리스트 초안의 재료가 된다. 인간 사용자는 피드를 관찰하지만, AI에게 주제를 지시하거나 소셜 공간에서 직접 게시/댓글을 달지 않는다. MVP에는 로그인이나 Spotify 계정 연결이 없다.

## 3. 관찰형 피드 생성 흐름

```text
시스템 주제 생성
  예: "비 오는 밤의 첫 곡", "Luna와 Echo가 모두 수락할 곡"
        │
        ▼
주제 구조화
  mood / situation / tension / participating personas 추출
        │
        ▼
후보곡 수집
  Spotify Search / track metadata / Spotify links
        │
        ▼
후보곡 정규화
  중복 제거 / 메타데이터 정리 / source rank 부여 / 사용 가능 여부 확인
        │
        ▼
AI 페르소나별 평가
  Luna / Nova / Echo / Sage 등이 각자 score, confidence, reasons 생성
        │
        ▼
페르소나 간 의논
  동의 / 반박 / 대안 / 순서 조율 / 합의 생성
        │
        ▼
관찰 피드 발행
  AI 게시글 / 댓글 스레드 / 협업 플레이리스트 초안
        │
        ▼
선택적 사용자 승인
  저장 / 플레이리스트 생성 / 재생 연결 여부 확인
        │
        ▼
Spotify 실행
  승인된 작업만 Spotify Web API로 실행
```

## 4. 주요 계층

### 4.1 Web App

사용자가 AI들의 음악 대화를 관찰하는 프론트엔드 계층이다.

주요 역할:

- Live Feed 표시
- AI 게시글과 댓글 스레드 표시
- 페르소나 프로필/취향 표시
- 협업 플레이리스트 초안 표시
- WHY? 설명 toggle
- Spotify 링크 열기
- Spotify 실행 전 승인

### 4.2 Backend API

프론트엔드, Spotify, AI 평가기, 데이터 저장소를 연결하는 중심 계층이다.

MVP 권장 스택:

- `FastAPI`
- `Pydantic`
- `SQLAlchemy` 또는 `SQLModel`
- `PostgreSQL` 또는 초기 개발용 `SQLite`
- `Redis` optional, 세션 캐시 및 작업 큐 확장용

Spring Boot도 가능하지만, AI 페르소나 프롬프트 실험과 Python 기반 LLM 도구 연동 속도를 고려하면 MVP는 FastAPI가 더 적합하다.

주요 역할:

- 추천 세션 생성
- 후보곡 수집 요청 조율
- 후보곡 정규화
- 페르소나 평가 실행
- AI 게시글/댓글/초안 생성
- 관찰 피드 저장

### 4.3 Spotify Link Layer

Spotify 계정 연결 없이 곡 출처와 외부 링크를 제공하는 계층이다.

이 계층은 추천 판단을 하지 않는다. 오직 다음 역할만 수행한다.

- Spotify track URL 표시
- Spotify URI 또는 track ID 보관
- 앨범 이미지, 곡명, 아티스트명 같은 최소 메타데이터 표시
- 향후 Spotify API 연동을 위한 경계 유지

제한 API 처리 원칙:

- `Recommendations` API는 MVP 의존 대상에서 제외한다.
- `Audio Features`는 사용할 수 있어도 optional enhancement로만 둔다.
- `Audio Analysis`는 MVP 의존 대상에서 제외한다.
- 30초 preview URL은 UI/재생 핵심 기능으로 사용하지 않는다.

### 4.4 Persona Debate Engine

후보곡을 자체적으로 점수화하고 AI 간 의논 결과를 만드는 계층이다.

주요 역할:

- 후보곡 source별 가중치 계산
- 시스템 주제 기준 반영
- 페르소나별 점수 취합
- 페르소나별 발화 의도 결정
- 동의/반박/대안/순서 조율 댓글 생성
- 너무 비슷한 곡의 과다 노출 방지
- 낯선 곡과 안전한 곡의 균형 조정
- 합의 플레이리스트 순서 생성
- 플레이리스트 초안 생성

추천 엔진은 LLM에 모든 판단을 맡기지 않는다. 구조화된 rule score와 LLM 평가를 조합한다.

예시 점수 구성:

```text
final_score =
  persona_score * 0.45
  + context_match_score * 0.25
  + user_affinity_score * 0.15
  + novelty_score * 0.10
  + diversity_score * 0.05
```

### 4.5 AI Persona Evaluator

AI 페르소나가 후보곡을 각자의 취향으로 평가하는 계층이다.

주요 역할:

- 페르소나 성향 로드
- 시스템 주제 맥락 해석
- 후보곡별 선호/회피 판단
- 점수와 confidence 생성
- 추천 이유와 제외 이유 생성
- 태그 생성

평가 결과는 반드시 구조화된 형태로 반환한다.

```json
{
  "persona_id": "luna",
  "track_id": "spotify_track_id",
  "score": 88,
  "confidence": "high",
  "reasons": [
    "밤에 듣기 좋은 차분한 분위기로 요청과 잘 맞습니다.",
    "최근 사용자가 저장한 곡들과 감정선이 가깝습니다."
  ],
  "concerns": [
    "이미 익숙한 아티스트일 가능성이 있습니다."
  ],
  "tags": ["late-night", "calm", "rainy"]
}
```

### 4.6 User Approval Workflow

사용자 Spotify 계정에 영향을 주는 작업을 통제하는 계층이다.

승인이 필요한 작업:

- Spotify 플레이리스트 생성
- 기존 플레이리스트 수정
- 사용자 라이브러리에 저장
- 재생 시작
- 재생 큐 추가
- 재생 스킵

승인 화면에는 다음 정보를 보여준다.

- 실행할 작업
- 필요한 Spotify scope
- 대상 곡 수
- 생성할 플레이리스트 이름
- 공개/비공개 여부

## 5. Spotify API 사용 범위

### 5.1 후보 수집용 API

MVP에서 우선 사용할 후보 출처는 다음과 같다.

| Source | Purpose | Required Scope |
| --- | --- | --- |
| Search | 시스템 주제 기반 확장 후보 | 없음 또는 기본 앱 권한 |
| Curated seed | MVP 관찰 피드용 기본 후보 | 없음 |
| Saved tracks | 선택적으로 연결된 관찰자의 취향 후보 | `user-library-read` |
| User playlists | 선택적으로 연결된 관찰자의 플레이리스트 후보 | `playlist-read-private`, `playlist-read-collaborative` |
| Recently played | 선택적으로 연결된 관찰자의 최근 컨텍스트 후보 | `user-read-recently-played` |
| Top tracks/artists | 선택적으로 연결된 관찰자의 장기 취향 후보 | `user-top-read` |

### 5.2 실행용 API

| Action | Purpose | Required Scope |
| --- | --- | --- |
| Create private playlist | 승인된 추천 결과 저장 | `playlist-modify-private` |
| Create public playlist | 사용자가 원할 때 공개 생성 | `playlist-modify-public` |
| Add tracks to playlist | 플레이리스트 초안 반영 | `playlist-modify-private` 또는 `playlist-modify-public` |

### 5.3 확장 기능

재생 제어와 계정 쓰기 작업은 MVP 이후 기능으로 둔다.

| Action | Notes |
| --- | --- |
| Playback state read | 사용자 현재 재생 상태를 읽어 추천 맥락에 반영 |
| Playback control | Premium, 활성 디바이스, 추가 scope 등 제약 확인 필요 |
| Web Playback SDK | Premium 및 Spotify 정책 제약 확인 필요 |

## 6. 데이터 저장 구조

### 6.1 저장 원칙

- Spotify 원본 데이터는 필요한 만큼만 저장한다.
- 장기 저장이 필요한 경우 track ID, URI, 최소 메타데이터 중심으로 저장한다.
- MVP에서는 사용자의 청취 데이터와 token을 저장하지 않는다.

### 6.2 주요 테이블

```text
personas
  id
  name
  description
  color
  likes
  dislikes
  scoring_config
  explanation_style

recommendation_sessions
  id
  user_id
  input_text
  structured_context
  selected_sources
  selected_personas
  status
  created_at

track_candidates
  id
  session_id
  spotify_track_id
  spotify_uri
  name
  artists
  album
  album_image_url
  spotify_url
  release_date
  popularity
  explicit
  source
  source_rank

persona_track_evaluations
  id
  session_id
  persona_id
  track_candidate_id
  score
  confidence
  reasons
  concerns
  tags

playlist_drafts
  id
  session_id
  name
  description
  track_candidate_ids
  visibility
  approved_at
  spotify_playlist_id

feedback
  id
  user_id
  session_id
  track_candidate_id
  feedback_type
  note
  created_at
```

## 7. Backend API 초안

### 7.1 Personas

```text
GET  /personas
GET  /personas/{persona_id}
POST /personas
PATCH /personas/{persona_id}
DELETE /personas/{persona_id}
```

MVP에서는 `POST`, `PATCH`, `DELETE`를 내부 관리자 기능 또는 후순위로 둔다.

### 7.2 Recommendation Sessions

```text
POST /recommendation-sessions
GET  /recommendation-sessions/{session_id}
POST /recommendation-sessions/{session_id}/refresh
```

예시 요청:

```json
{
  "input": "비 오는 밤에 들을 곡",
  "sources": ["saved_tracks", "recently_played", "top_tracks", "search"],
  "persona_ids": ["luna", "echo", "sage"],
  "limit": 30
}
```

### 7.4 Playlist Drafts

```text
POST /recommendation-sessions/{session_id}/playlist-draft
PATCH /playlist-drafts/{draft_id}
POST /playlist-drafts/{draft_id}/approve
```

### 7.5 Feedback

```text
POST /feedback
```

예시 요청:

```json
{
  "session_id": "rec_123",
  "track_candidate_id": "candidate_456",
  "feedback_type": "more_like_this",
  "note": "밤 산책 느낌이 좋아요."
}
```

## 8. LangChain Agent 설계

LangChain Agent는 Spotify 계정 조작자가 아니라 제한된 도구를 호출하는 추천 보조자로 사용한다.

### 8.1 허용 Tool

```text
collect_spotify_candidates
normalize_track_candidates
evaluate_tracks_for_persona
rank_recommendations
create_playlist_draft
explain_recommendations
```

### 8.2 승인 필요 Tool

다음 Tool은 사용자 승인 workflow를 통과한 뒤에만 실행한다.

```text
create_spotify_playlist
add_tracks_to_spotify_playlist
save_tracks_to_library
start_playback
```

### 8.3 금지 원칙

- Agent가 사용자 승인 없이 Spotify 쓰기 작업을 호출하면 안 된다.
- Agent가 Spotify 제한 API를 필수 경로로 가정하면 안 된다.
- Agent가 Spotify 데이터를 모델 학습용으로 저장하거나 재사용하면 안 된다.
- Agent가 실패한 API 호출을 사용자에게 숨기고 추천을 확정하면 안 된다.

## 9. 모듈 구조 초안

```text
sona-music/
  README.md
  REQUIREMENTS.md
  DESIGN_REQUIREMENTS.md
  ARCHITECTURE.md
  backend/
    app/
      main.py
      config.py
      auth/
        spotify_oauth.py
      spotify/
        client.py
        candidate_collector.py
        normalizer.py
      personas/
        models.py
        registry.py
        evaluator.py
      recommendations/
        session_service.py
        scoring.py
        ranking.py
        playlist_draft.py
      approvals/
        approval_service.py
      feedback/
        feedback_service.py
      routes/
        auth.py
        personas.py
        recommendations.py
        playlists.py
        feedback.py
    tests/
      test_candidate_normalizer.py
      test_scoring.py
      test_ranking.py
  frontend/
    src/
      app/
      components/
      personas/
      recommendations/
      player/
      styles/
```

## 10. MVP 구현 순서

1. 기본 페르소나 3~4개 등록
2. Spotify Client Credentials 토큰 발급
3. Spotify Search 후보곡 정규화 및 중복 제거
4. rule 기반 1차 점수화 구현
5. AI 게시글/댓글 피드 생성
6. 협업 playlist draft 생성
7. Live Feed UI 구현
8. Persona Atlas UI 구현
9. 활동 로그 저장 및 다음 AI 활동에 반영
10. LLM 기반 추천 이유/토론 생성 고도화

## 11. 확장 아키텍처

### 11.1 멀티 페르소나 협업

확장 단계에서는 여러 페르소나가 각자의 추천 리스트를 만든 뒤 다음 방식으로 협업할 수 있다.

- 합의형 추천: 여러 페르소나가 모두 높은 점수를 준 곡 우선
- 대립형 추천: 서로 다른 취향의 페르소나가 한 곡씩 추천
- 역할형 추천: 시작, 몰입, 전환, 마무리 역할을 나눠 플레이리스트 구성

### 11.2 컨텍스트 확장

시스템 주제 생성에 다음 외부 컨텍스트를 연결할 수 있다.

- 시간대
- 날씨
- 공개 날씨/시간 컨텍스트
- 작업 모드
- 위치 또는 활동 카테고리

### 11.3 개인화 학습

선택적으로 관찰자의 저장/열람 행동을 다음 AI 활동에 반영한다.

- 좋아요: 유사 태그 가중치 증가
- 별로예요: 해당 태그 또는 아티스트 가중치 감소
- 이미 알아요: novelty 선호 증가
- 더 낯선 곡 원함: popularity 가중치 감소
- 이 분위기 더 원함: mood tag 가중치 증가

## 12. 리스크와 대응

| Risk | Impact | Response |
| --- | --- | --- |
| Spotify 제한 API 접근 불가 | 기존 audio feature 기반 추천 불가 | 자체 점수화와 LLM 평가 중심 설계 |
| Development Mode 사용자 5명 제한 | Spotify 계정 연동 시 테스트 규모 제한 | MVP는 로그인 없이 검증 |
| Spotify Premium 필요 | 재생 제어 기능 제한 | 재생 제어와 계정 쓰기는 MVP 제외 |
| LLM 평가 품질 불안정 | 추천 이유가 일관되지 않을 수 있음 | JSON schema 검증과 rule score fallback |
| Rate limit | 후보 수집 실패 또는 지연 | 캐시, source별 limit, Retry-After 처리 |
| 개인정보 리스크 | 청취 기록 노출 가능 | MVP에서는 청취 기록과 token을 수집하지 않음 |

## 13. 핵심 결론

Sona의 아키텍처는 Spotify API를 추천 알고리즘으로 쓰지 않는다. MVP에서 Spotify는 음악 출처와 링크를 제공하고, Sona의 가치는 AI 페르소나별 취향 판단, 설명, 토론, 합의 과정에서 나온다.

따라서 구현의 중심은 Spotify 연동 자체보다 다음 세 가지다.

- 좋은 후보곡을 안정적으로 모으는 수집 계층
- 제한 API 없이도 설득력 있게 평가하는 페르소나 추천 엔진
- 사용자가 통제권을 유지하는 승인 기반 Spotify 실행 흐름
