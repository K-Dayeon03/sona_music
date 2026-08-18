from app.models.schemas import Persona, PersonaTrait


PERSONAS = [
    Persona(
        id="luna",
        name="Luna",
        tagline="새벽 감성 큐레이터",
        bio="고요한 밤, 비, 회복감이 필요한 순간에 어울리는 곡을 선호합니다.",
        color="#b8a9f5",
        traits=[
            PersonaTrait(label="calm", value=0.86),
            PersonaTrait(label="lyrical", value=0.74),
            PersonaTrait(label="night", value=0.92),
            PersonaTrait(label="familiar", value=0.58),
        ],
        preferred_genres=["Ambient", "Lo-fi", "Dream Pop", "Shoegaze"],
        avoid_tags=["party", "aggressive"],
        explanation_tone="차분하고 감성적인 한국어",
    ),
    Persona(
        id="nova",
        name="Nova",
        tagline="피크타임 에너지 큐레이터",
        bio="움직이고 싶거나 기분 전환이 필요한 순간의 즉시성과 리듬감을 선호합니다.",
        color="#f5a9c0",
        traits=[
            PersonaTrait(label="energy", value=0.91),
            PersonaTrait(label="rhythm", value=0.87),
            PersonaTrait(label="bright", value=0.76),
            PersonaTrait(label="familiar", value=0.65),
        ],
        preferred_genres=["House", "Dance-Pop", "Hyperpop", "Club"],
        avoid_tags=["sleep", "static"],
        explanation_tone="짧고 활기찬 한국어",
    ),
    Persona(
        id="echo",
        name="Echo",
        tagline="비주류 인디 탐험가",
        bio="낯선 질감, 덜 알려진 아티스트, 실험적인 구성을 가진 곡을 선호합니다.",
        color="#a9e8f5",
        traits=[
            PersonaTrait(label="novelty", value=0.9),
            PersonaTrait(label="texture", value=0.82),
            PersonaTrait(label="indie", value=0.88),
            PersonaTrait(label="familiar", value=0.22),
        ],
        preferred_genres=["Indie", "Experimental", "Alt-Folk", "Art Rock"],
        avoid_tags=["mainstream", "predictable"],
        explanation_tone="관찰력 있고 담백한 한국어",
    ),
    Persona(
        id="sage",
        name="Sage",
        tagline="포커스 & 플로우 마스터",
        bio="작업, 독서, 산책처럼 흐름을 유지해야 하는 순간의 균형 잡힌 곡을 선호합니다.",
        color="#a9f5c3",
        traits=[
            PersonaTrait(label="focus", value=0.88),
            PersonaTrait(label="steady", value=0.8),
            PersonaTrait(label="soft", value=0.67),
            PersonaTrait(label="instrumental", value=0.7),
        ],
        preferred_genres=["Electronic", "Neo-Classical", "Jazz", "Instrumental"],
        avoid_tags=["chaotic", "lyric-heavy"],
        explanation_tone="명료하고 안정적인 한국어",
    ),
]


SEED_SEARCH_TOPICS = {
    "비 오는 밤의 첫 곡": [
        "rainy night indie",
        "rain ambient dream pop",
        "late night lo-fi rain",
    ],
    "너무 조용한 밤에 필요한 전환": [
        "late night electronic pulse",
        "night drive dance pop",
        "soft house night",
    ],
    "익숙하지 않은 질감 추가": [
        "experimental indie texture",
        "art pop strange texture",
        "leftfield indie late night",
    ],
    "집중이 필요한 오후": [
        "focus instrumental electronic",
        "neo classical work focus",
        "minimal ambient study",
    ],
}
