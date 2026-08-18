# Sona 디자인 요구사항

## 1. 디자인 목표

Sona는 AI 음악 페르소나가 각자의 취향으로 Spotify 후보곡을 큐레이션하는 음악 서비스다. 화면은 어두운 음악 앱 분위기를 기반으로 하되, 각 AI 페르소나의 고유 색상을 통해 캐릭터성과 추천 맥락을 즉시 구분할 수 있어야 한다.

핵심 디자인 원칙은 다음과 같다.

- 전체 배경은 깊은 다크 톤으로 유지한다.
- 주요 CTA, 로고, 네비게이션 강조에는 `#ECEE81`을 제한적으로 사용한다.
- 각 AI 페르소나는 하나의 고유 컬러를 가진다.
- 페르소나 컬러는 배경 tint, 테두리, 텍스트 강조에 투명도 변형으로 일관되게 사용한다.
- 수치, 태그, BPM, popularity 같은 데이터성 정보는 monospace로 표현한다.
- 유리 질감의 카드와 blur는 제한적으로 사용해 음악 앱 특유의 몰입감을 만든다.

## 2. 컬러 팔레트

### 2.1 기본 색상

| Token | Value | Usage |
| --- | --- | --- |
| Background | `#0c0c0e` | Page background |
| Surface 1 | `rgba(255,255,255,0.03)` | Card / section background |
| Surface 2 | `rgba(255,255,255,0.05)` | Hover state |
| Border | `rgba(255,255,255,0.07)` | Card borders, dividers |
| Accent | `#ECEE81` | Primary CTA, logo, highlights |
| Accent dim | `rgba(236,238,129,0.1)` | Accent background tint |
| Text primary | `#f0f0f0` | Headings, body |
| Text secondary | `rgba(255,255,255,0.45)` | Subtitles, descriptions |
| Text muted | `rgba(255,255,255,0.3)` | Labels, captions |
| Text faint | `rgba(255,255,255,0.25)` | Metadata, secondary numbers |

### 2.2 페르소나 색상

| Persona | Color | Usage |
| --- | --- | --- |
| Luna | `#b8a9f5` | Purple, calm late-night vibe |
| Nova | `#f5a9c0` | Pink, high-energy dance |
| Echo | `#a9e8f5` | Sky blue, indie underground |
| Sage | `#a9f5c3` | Mint green, focus and instrumental |

각 페르소나 컬러는 다음 패턴으로 파생한다.

- 배경 tint: `${color}10` ~ `${color}18`
- 테두리: `${color}25` ~ `${color}60`
- 텍스트/강조: 원색 그대로

## 3. 타이포그래피

| Role | Font | Weight | Usage |
| --- | --- | --- | --- |
| Display | `Outfit` | 700-900 | 헤더, 카드 제목, 페르소나 이름 |
| Body | `Inter` | 400-500 | 설명, 트랙 정보 |
| Mono | `DM Mono` | 300-500 | BPM, 수치, 태그, 라벨 |

### 3.1 Google Fonts import

`index.css` 최상단에 다음 순서로 import한다.

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
@import 'tailwindcss';
```

## 4. 레이아웃 구조

```text
<App>
├── <header>             sticky nav, blur backdrop, logo + nav tabs
├── <main>               max-w-3xl mx-auto px-4
│   ├── Hero section     centered text, CTA buttons
│   ├── Live Feed        AI persona discussion cards
│   ├── Collab drafts    Spotify track consensus drafts
│   ├── Stats row        3-col grid
│   ├── Persona grid     2-col responsive grid, sm:grid-cols-2
│   ├── Persona detail   selected AI full profile + decision traits
│   └── Collab section   2-col grid with image background cards
└── <SpotifyEmbedBar>    fixed bottom, Spotify iframe embed
```

### 4.1 반응형 규칙

- 모바일은 기본 1-column 레이아웃을 사용한다.
- `sm` 이상, 즉 640px 이상에서는 페르소나 그리드와 협업 섹션을 2-column으로 전환한다.
- 메인 콘텐츠 폭은 `max-w-3xl mx-auto px-4`를 기본으로 한다.
- 하단 고정 Spotify Embed Bar와 콘텐츠가 겹치지 않도록 main 하단 padding을 확보한다.

## 5. 컴포넌트 패턴

### 5.1 Glass Card

기본 카드 스타일:

```css
background: rgba(255,255,255,0.03);
border: 1.5px solid rgba(255,255,255,0.07);
border-radius: 1rem;
```

상태:

- Hover: `rgba(255,255,255,0.05)` 배경과 `translateY(-2px)`
- Active selected: `${personaColor}18` 배경과 `${personaColor}60` 테두리

### 5.2 Feature Bar, Audio DNA

Feature Bar는 페르소나의 음악 취향 수치를 보여주는 얇은 막대 UI다.

- 높이: `4px`
- border-radius: `2px`
- track: `rgba(255,255,255,0.1)`
- fill: persona color
- transition: `width 0.6s cubic-bezier(0.34,1.56,0.64,1)`
- label: `DM Mono`, `10px`, uppercase, tracking-widest
- value: `DM Mono`, `10px`, right-aligned

### 5.3 Tag / Badge

```css
font-family: 'DM Mono', monospace;
font-size: 9px;
padding: 2px 8px;
border-radius: 9999px;
background: ${color}18;
color: ${color};
```

허용 범위:

- font-size: `9px` ~ `10px`
- 태그는 과하게 많이 노출하지 않고 카드당 핵심 2~4개만 보여준다.

### 5.4 Track Row

Track Row는 다음 4개 영역의 flex 구조를 사용한다.

```text
[index/wave | album art 40px | title + artist | controls]
```

상태:

- Hover: Surface 2 배경
- Playing: wave icon과 persona color 텍스트 적용
- WHY? 버튼: toggle로 큐레이션 설명을 펼친다.
- 큐레이션 설명 영역: persona color 기반 `border-left`를 사용한다.

### 5.5 Now Playing Bar

```css
position: fixed;
bottom: 0;
left: 0;
right: 0;
background: rgba(18,18,20,0.95);
backdrop-filter: blur(20px);
border: 1px solid ${persona.color}30;
border-radius: 1rem;
```

규칙:

- 화면 하단에 고정한다.
- 현재 재생 중인 페르소나 컬러를 테두리와 강조에 사용한다.
- 작은 화면에서는 곡명, 아티스트, 핵심 컨트롤이 먼저 보이도록 우선순위를 둔다.

## 6. 애니메이션 패턴

| Name | Class | Description |
| --- | --- | --- |
| Wave bars | `.wave-bar` | 5개 bar, height 4px -> 20px, 0.8s loop |
| Float | `.float-anim` | translateY 0 -> -8px, 4s ease-in-out |
| Pulse ring | `.pulse-ring` | scale 0.9 -> 1.4, opacity 1 -> 0 |
| Spin slow | `.spin-slow` | 360deg, 12s linear infinite |

애니메이션 사용 원칙:

- 음악 재생, 선택, 현재 상태를 나타내는 곳에만 사용한다.
- 배경 장식용 애니메이션은 최소화한다.
- 사용자의 시선을 빼앗지 않도록 반복 애니메이션은 작고 부드럽게 유지한다.

## 7. 주요 디자인 결정

- 다크 배경: Spotify와 음악 앱 표준에 가까운 몰입형 배경을 사용한다.
- 페르소나 컬러 시스템: 각 AI마다 고유 색상 1개를 부여하고 투명도 변형으로 일관성을 유지한다.
- 단일 포인트 Accent: `#ECEE81`은 네비게이션, CTA, 로고에만 제한적으로 사용한다.
- 데이터 정보용 Mono: BPM, popularity, 점수, 태그, 라벨은 `DM Mono`로 표현한다.
- 제한적 blur: `backdrop-filter blur`는 sticky nav와 Now Playing Bar에만 적용한다.
- 2-column responsive grid: 모바일은 1-column, 640px 이상은 2-column을 기본으로 한다.

## 8. 구현 체크리스트

- [ ] CSS 변수 또는 Tailwind theme token으로 기본 컬러를 등록한다.
- [ ] 페르소나 컬러를 데이터 구조로 관리한다.
- [ ] `Outfit`, `Inter`, `DM Mono`를 `index.css` 최상단에서 import한다.
- [ ] 카드, 태그, Feature Bar, Track Row, Now Playing Bar를 재사용 가능한 컴포넌트로 만든다.
- [ ] hover, selected, playing 상태를 모두 구현한다.
- [ ] WHY? 설명 toggle을 구현한다.
- [ ] 모바일 1-column, `sm` 이상 2-column 반응형을 확인한다.
- [ ] Now Playing Bar와 main 콘텐츠가 겹치지 않는지 확인한다.
- [ ] Accent 컬러가 CTA/로고/하이라이트 외에 과도하게 쓰이지 않는지 확인한다.
