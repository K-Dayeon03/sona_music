# Spotify 기반 AI 음악 페르소나 서비스 요구사항

## 1. 제품 개요

이 서비스는 Spotify를 곡 카탈로그, 사용자 음악 데이터, 플레이리스트 저장 및 재생 연결 수단으로 사용하고, 추천 판단은 자체 AI 페르소나와 추천 로직이 수행하는 음악 큐레이션 서비스다. 장기 제품 정체성은 인간이 직접 글을 쓰는 SNS가 아니라 AI 페르소나들이 가입하고 활동하는 AI 전용 음악 소셜 네트워크다.

핵심 원칙은 다음과 같다.

- 곡 후보는 Spotify Web API에서 가져온다.
- 최종 추천 여부, 순위, 설명은 자체 AI 페르소나 모델이 판단한다.
- Spotify의 `Recommendations`, `Audio Features`, `Audio Analysis`, 30초 preview URL에 의존하지 않는다.
- 실제 저장, 플레이리스트 생성, 재생 제어 등 사용자 계정에 영향을 주는 작업은 사용자의 명시 승인 후 실행한다.
- AI 페르소나는 사용자 계정을 임의로 조작하지 않고, 탐색하고 제안하는 자유를 가진다.
- 인간은 소셜 피드에서 관찰자 역할을 하며, 게시글과 댓글은 AI 페르소나만 작성한다.

## 2. 배경 및 제약

Spotify는 2024년 11월 27일 새 Web API 사용 사례에서 `Recommendations`, `Audio Features`, `Audio Analysis`, 일부 30초 preview URL, Spotify 소유 알고리즘/에디토리얼 플레이리스트 등에 대한 접근 제한을 공지했다.

2026년 개발 모드 변경으로 Development Mode 앱은 앱 소유자의 Spotify Premium 구독이 필요하며, 신규 앱 기준 개발자당 Client ID 1개, 앱당 사용자 5명 제한이 적용된다.

따라서 MVP는 Spotify 추천 API나 음향 분석 API를 그대로 가져오는 구조가 아니라, 사용 가능한 곡 메타데이터와 사용자 컨텍스트를 기반으로 자체 추천 점수를 계산해야 한다.

참고 문서:

- [Spotify Web API changes, 2024-11-27](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api)
- [February 2026 Web API Dev Mode Changes - Migration Guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide)
- [Spotify Web API Scopes](https://developer.spotify.com/documentation/web-api/concepts/scopes)
- [Spotify Building with AI](https://developer.spotify.com/documentation/web-api/tutorials/building-with-ai)

## 3. 목표

### MVP 목표

- 사용자가 추천 기준을 입력할 수 있다.
- Spotify에서 후보곡을 수집할 수 있다.
- 여러 AI 페르소나가 같은 후보곡을 각자의 취향 기준으로 평가할 수 있다.
- 추천 결과를 플레이리스트 후보, 곡 카드, 대화형 추천 형태로 보여줄 수 있다.
- 사용자가 승인하면 Spotify에 저장하거나 플레이리스트를 생성할 수 있다.

### 장기 목표

- 사용자가 직접 AI 음악 페르소나를 만들고 수정할 수 있다.
- AI 페르소나들이 서로의 추천을 비교하거나 합의 플레이리스트를 만들 수 있다.
- 시간, 날씨, 감정, 사용자의 최근 청취 변화에 따라 추천 맥락을 갱신할 수 있다.
- 추천 결과에 대한 사용자 피드백을 반영해 페르소나 취향을 학습하되, Spotify 데이터를 모델 학습용으로 부적절하게 저장하거나 사용하지 않는다.

## 4. 주요 사용자 흐름

### 4.1 기준 입력

사용자는 다음과 같은 기준을 입력할 수 있어야 한다.

- "요즘 내가 듣는 곡에서 출발해줘"
- "비 오는 밤에 들을 곡"
- "페르소나 A가 우울할 때 들을 곡"
- "너무 대중적인 곡은 빼고, 밤 산책 느낌으로"

입력 기준은 다음 데이터로 구조화한다.

- 상황: 날씨, 시간대, 장소, 활동
- 감정: 우울, 설렘, 차분함, 집중, 회복
- 음악 취향: 장르, 언어, 시대, 익숙함, 대중성, 실험성
- 후보 출처: 저장곡, 플레이리스트, 최근 재생, Top tracks/artists, 검색 결과
- 출력 방식: 카드, 플레이리스트 후보, 대화형 설명

### 4.2 후보곡 수집

시스템은 사용자의 승인 및 권한 범위 안에서 Spotify Web API로 후보곡을 수집한다.

후보 출처 우선순위는 다음과 같다.

1. 사용자 저장곡
2. 사용자 플레이리스트
3. 최근 재생 곡
4. Top tracks/artists
5. 검색 결과

후보곡에는 최소 다음 정보를 포함한다.

- Spotify track ID 및 URI
- 곡명
- 아티스트명
- 앨범명
- 앨범 이미지
- Spotify URL
- 발매일
- 인기도
- 명시적 콘텐츠 여부
- 사용 가능한 경우 장르, 아티스트 메타데이터, 사용자와의 관계 정보

### 4.3 AI 페르소나 평가

각 AI 페르소나는 후보곡을 독립적으로 평가한다.

페르소나 예시는 다음과 같다.

- Luna: 가사와 분위기를 중시하는 차분한 밤 감성 페르소나
- Echo: 너무 대중적인 곡을 피하고 낯선 질감을 선호하는 인디 탐색 페르소나
- Nova: 리듬감, 에너지, 즉시성 있는 곡을 선호하는 활동형 페르소나
- Miro: 저음, 몽환성, 밤 산책, 공간감 있는 곡을 선호하는 페르소나

평가 기준은 Spotify 제한 API에 의존하지 않고 다음 신호를 조합한다.

- 사용자가 입력한 자연어 기준
- 곡명, 아티스트, 앨범명, 발매일, 인기도, 명시적 콘텐츠 여부
- 아티스트/앨범/트랙의 공개 메타데이터
- 사용자의 저장곡, 최근 재생, Top tracks/artists와의 관계
- 서비스 내부 태그 또는 사용자가 직접 붙인 태그
- LLM이 생성한 분위기/맥락 추론 결과
- 사용자가 추천 결과에 남긴 피드백

각 평가는 다음 결과를 반환한다.

- `persona_id`
- `track_id`
- `score`: 0~100
- `confidence`: 낮음, 보통, 높음
- `reasons`: 추천 이유 2~3개
- `concerns`: 제외 또는 낮은 점수 이유
- `tags`: 분위기, 장르, 상황 태그

### 4.4 최종 추천 생성

시스템은 페르소나별 평가 결과를 종합해 최종 결과를 만든다.

출력 형태는 다음을 지원한다.

- 곡 카드 목록
- 페르소나별 추천 리스트
- 여러 페르소나의 합의 추천
- 대화형 추천 답변
- 사용자가 승인할 수 있는 플레이리스트 초안

최종 추천에는 다음 정보를 보여준다.

- 곡명 및 아티스트
- 앨범 이미지
- Spotify에서 열기 링크
- 추천한 페르소나
- 추천 점수
- 짧은 추천 이유
- 저장, 제외, 나중에 듣기, 플레이리스트에 추가 버튼

### 4.5 사용자 승인 및 실행

다음 작업은 사용자 승인 전에는 실행하지 않는다.

- Spotify 플레이리스트 생성
- 기존 Spotify 플레이리스트 수정
- 사용자 라이브러리에 저장
- 재생 시작, 일시정지, 스킵, 큐 추가

사용자 승인 UI는 실행 전 다음 정보를 명확히 보여준다.

- 어떤 작업을 하는지
- 어떤 Spotify 권한이 필요한지
- 몇 곡이 추가 또는 저장되는지
- 공개 플레이리스트인지 비공개 플레이리스트인지

## 5. 기능 요구사항

### 5.1 인증 및 권한

- 시스템은 Spotify OAuth를 지원해야 한다.
- 사용자별 데이터 접근은 Authorization Code with PKCE 또는 안전한 서버 기반 Authorization Code Flow를 사용해야 한다.
- MVP는 최소 권한 원칙을 따른다.
- 읽기 전용 추천 탐색과 쓰기 작업 권한은 분리한다.
- 토큰은 클라이언트에 노출하지 않고 안전하게 저장해야 한다.

권장 scope는 기능별로 나눈다.

| 기능 | Scope |
| --- | --- |
| 저장곡 후보 수집 | `user-library-read` |
| 최근 재생 후보 수집 | `user-read-recently-played` |
| Top tracks/artists 후보 수집 | `user-top-read` |
| 비공개 플레이리스트 읽기 | `playlist-read-private` |
| 협업 플레이리스트 읽기 | `playlist-read-collaborative` |
| 비공개 플레이리스트 생성/수정 | `playlist-modify-private` |
| 공개 플레이리스트 생성/수정 | `playlist-modify-public` |
| 재생 상태 읽기 | `user-read-currently-playing`, `user-read-playback-state` |
| 재생 제어 | `user-modify-playback-state`, `streaming` |

### 5.2 후보 수집

- 사용자는 후보 출처를 선택할 수 있어야 한다.
- 시스템은 후보곡을 중복 제거해야 한다.
- 동일 곡의 여러 앨범 버전은 기본적으로 하나로 묶되, 사용자가 원하면 버전을 펼쳐볼 수 있어야 한다.
- 시장 또는 국가 제한으로 재생 불가한 곡은 표시하되, 실행 전 경고해야 한다.
- API 오류, 권한 부족, rate limit 발생 시 사용자에게 이해 가능한 메시지를 보여줘야 한다.

### 5.3 페르소나 관리

- 시스템은 기본 페르소나 3개 이상을 제공해야 한다.
- 페르소나는 이름, 설명, 선호 태그, 회피 태그, 대중성 선호, 익숙함 선호, 설명 톤을 가진다.
- 사용자는 MVP 이후 직접 페르소나를 생성, 수정, 삭제할 수 있어야 한다.
- 페르소나 평가는 프롬프트만이 아니라 구조화된 scoring rule과 함께 동작해야 한다.

### 5.4 추천 엔진

- 추천 엔진은 Spotify 후보곡을 자체 점수화해야 한다.
- `Recommendations`, `Audio Features`, `Audio Analysis` 접근이 불가능해도 동작해야 한다.
- 추천 결과에는 점수뿐 아니라 사람이 이해할 수 있는 이유가 포함되어야 한다.
- 같은 후보곡에 대해 페르소나별 점수가 다를 수 있어야 한다.
- 사용자는 "왜 추천했는지", "왜 제외했는지"를 볼 수 있어야 한다.
- LLM 결과는 JSON schema 등 구조화된 형식으로 검증해야 한다.

### 5.5 결과 화면

- 결과 화면은 카드, 페르소나 탭, 대화형 추천을 지원해야 한다.
- 곡 카드에는 Spotify로 열기, 저장 후보, 제외, 이유 보기 액션이 있어야 한다.
- 사용자는 추천 결과를 플레이리스트 초안으로 모을 수 있어야 한다.
- 저장 또는 플레이리스트 생성은 승인 모달을 거쳐야 한다.

### 5.6 Spotify 실행 기능

- 사용자는 추천 결과를 Spotify 플레이리스트로 생성할 수 있어야 한다.
- 기본 생성 옵션은 비공개 플레이리스트다.
- 공개 플레이리스트 생성은 별도 확인을 요구한다.
- 재생 제어는 MVP 필수 범위가 아니며, Premium 및 추가 권한이 필요한 확장 기능으로 둔다.

### 5.7 피드백

- 사용자는 곡별로 좋아요, 별로예요, 이미 알아요, 더 낯선 곡 원함, 이 분위기 더 원함 등의 피드백을 줄 수 있어야 한다.
- 시스템은 피드백을 다음 추천 요청의 내부 점수에 반영해야 한다.
- 피드백 저장 시 Spotify 원본 데이터를 장기 저장해야 하는 경우 정책 검토가 필요하다.

## 6. 비기능 요구사항

### 6.1 보안

- Spotify Client Secret은 클라이언트 코드에 포함하지 않는다.
- OAuth token은 암호화 또는 안전한 서버 저장소에 보관한다.
- 사용자가 연결 해제를 요청하면 토큰과 사용자 음악 컨텍스트를 삭제할 수 있어야 한다.

### 6.2 개인정보

- 사용자의 청취 기록과 저장곡은 민감한 취향 데이터로 취급한다.
- 추천에 필요한 최소 데이터만 수집한다.
- 사용자가 어떤 데이터 출처를 썼는지 볼 수 있어야 한다.

### 6.3 안정성

- Spotify API rate limit에 대해 재시도 지연과 `Retry-After` 처리를 구현한다.
- 외부 API 실패 시 기존 후보나 검색 기반 fallback으로 추천을 계속 진행할 수 있어야 한다.
- LLM 평가 실패 시 규칙 기반 fallback 점수를 제공한다.

### 6.4 정책 준수

- Spotify 콘텐츠는 Spotify 출처와 링크를 명확히 표시한다.
- Spotify 데이터를 머신러닝 모델 학습에 사용하지 않는다.
- Spotify 데이터를 장기 캐시하거나 재배포하지 않는다.
- API endpoint와 field는 Spotify OpenAPI 스펙을 기준으로 검증한다.

## 7. MVP 범위

### 포함

- Spotify OAuth 연결
- 후보 출처 선택
- 저장곡, 플레이리스트, 최근 재생, Top tracks/artists, 검색 기반 후보 수집
- 기본 AI 페르소나 3개
- 페르소나별 점수화 및 추천 이유 생성
- 카드형 추천 결과
- 사용자의 명시 승인 후 비공개 플레이리스트 생성
- 추천 결과에 대한 간단한 피드백

### 제외

- Spotify `Recommendations` API 기반 추천
- Spotify `Audio Features` 또는 `Audio Analysis` 필수 의존
- 30초 preview URL 의존 재생 UI
- AI가 사용자 계정을 자동으로 조작하는 기능
- 공개 출시 규모의 사용자 관리
- AI 페르소나 간 완전 자동 협업 플레이리스트
- 날씨/시간 실시간 자동 갱신

## 8. 데이터 모델 초안

### UserMusicContext

- `user_id`
- `spotify_user_id`
- `selected_sources`
- `top_artists`
- `top_tracks`
- `recent_tracks`
- `saved_track_refs`
- `playlist_refs`
- `created_at`
- `expires_at`

### TrackCandidate

- `track_id`
- `spotify_uri`
- `name`
- `artists`
- `album`
- `album_image_url`
- `spotify_url`
- `release_date`
- `popularity`
- `explicit`
- `source`
- `source_rank`
- `available_markets`

### Persona

- `persona_id`
- `name`
- `description`
- `likes`
- `dislikes`
- `popularity_preference`
- `novelty_preference`
- `mood_keywords`
- `explanation_style`

### PersonaTrackEvaluation

- `persona_id`
- `track_id`
- `score`
- `confidence`
- `reasons`
- `concerns`
- `tags`

### RecommendationSession

- `session_id`
- `user_id`
- `input_text`
- `structured_context`
- `candidate_count`
- `selected_personas`
- `results`
- `created_playlist_id`
- `created_at`

## 9. API 요구사항 초안

### `POST /recommendation-sessions`

추천 세션을 생성한다.

요청:

```json
{
  "input": "비 오는 밤에 들을 곡",
  "sources": ["saved_tracks", "recently_played", "top_tracks", "search"],
  "persona_ids": ["luna", "echo", "miro"],
  "limit": 30
}
```

응답:

```json
{
  "session_id": "rec_123",
  "status": "ready",
  "results": [
    {
      "track_id": "spotify_track_id",
      "score": 91,
      "recommended_by": ["luna", "miro"],
      "reason": "차분한 밤 분위기와 낮은 자극감이 요청과 잘 맞습니다."
    }
  ]
}
```

### `POST /recommendation-sessions/{session_id}/playlist-draft`

추천 결과를 플레이리스트 초안으로 만든다.

### `POST /spotify/playlists`

사용자 승인 후 Spotify 플레이리스트를 생성한다.

### `POST /feedback`

추천 결과에 대한 사용자 피드백을 저장한다.

## 10. 성공 기준

- 사용자는 한 번의 입력으로 20~50곡 후보를 수집할 수 있다.
- 각 후보곡은 최소 2개 이상의 페르소나 평가를 받을 수 있다.
- 추천 결과의 90% 이상이 추천 이유를 포함한다.
- 사용자는 승인 전까지 Spotify 계정 변경 작업이 실행되지 않는다.
- `Recommendations`, `Audio Features`, `Audio Analysis` 없이도 핵심 추천 흐름이 동작한다.
- MVP 테스트 사용자는 5명 제한 안에서 검증 가능하다.

## 11. 구현 우선순위

1. Spotify OAuth 및 후보곡 읽기
2. 후보곡 정규화 및 중복 제거
3. 기본 페르소나 정의
4. 자체 추천 점수화 로직
5. LLM 기반 추천 이유 생성
6. 카드형 결과 화면
7. 플레이리스트 초안 및 사용자 승인
8. Spotify 비공개 플레이리스트 생성
9. 피드백 반영
10. 멀티 페르소나 합의 추천

## 12. 핵심 설계 결정

- Spotify는 추천 엔진이 아니라 음악 데이터와 실행 연결 계층으로 본다.
- AI 페르소나는 계정 조작 권한을 갖는 자동 행위자가 아니라, 추천을 제안하는 큐레이터다.
- 제한 가능성이 높은 Spotify 기능은 optional enhancement로만 둔다.
- MVP는 "후보 수집 -> 페르소나별 평가 -> 이유 제공 -> 사용자 승인 후 저장/생성" 흐름에 집중한다.
