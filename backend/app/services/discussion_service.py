from dataclasses import dataclass
from typing import List, Sequence, Set

from fastapi import HTTPException, status

from app.data.seed import PERSONAS, SEED_SEARCH_TOPICS
from app.models.schemas import (
    AiCollabPlaylist,
    AiCollabTrack,
    AiSocialComment,
    AiSocialPost,
    CandidateTrack,
    GeneratedDiscussion,
    Persona,
)
from app.services.spotify_catalog_service import search_tracks_for_queries


TOPIC_TAG_HINTS = {
    "비": {"rain", "calm", "night"},
    "밤": {"night", "late-night", "calm"},
    "새벽": {"night", "late-night", "quiet"},
    "산책": {"walk", "city", "steady"},
    "집중": {"focus", "steady", "instrumental", "work"},
    "일": {"focus", "work", "steady"},
    "공부": {"focus", "steady", "soft"},
    "운동": {"energy", "rhythm", "bright"},
    "댄스": {"dance", "rhythm", "energy"},
    "신나는": {"energy", "bright", "rhythm"},
    "인디": {"indie", "novelty", "texture"},
    "낯선": {"novelty", "experimental", "texture"},
    "우울": {"calm", "lyrical", "night"},
}


PERSONA_TAGS = {
    "luna": {"calm", "night", "late-night", "lyrical", "dreamy", "rain", "quiet"},
    "nova": {"energy", "rhythm", "bright", "dance", "city"},
    "echo": {"indie", "novelty", "texture", "experimental", "strange"},
    "sage": {"focus", "steady", "instrumental", "soft", "work", "walk"},
}


PERSONA_ROLES = {
    "luna": "정서적 시작",
    "echo": "낯선 질감",
    "nova": "에너지 전환",
    "sage": "흐름 정리",
}

PERSONA_VOICES = {
    "luna": {
        "lens": "공기, 여백, 감정선",
        "risk": "너무 밝거나 선명하면 밤의 결이 깨짐",
    },
    "echo": {
        "lens": "낯섦, 표면의 결, 발견감",
        "risk": "너무 안전하면 기억점이 사라짐",
    },
    "nova": {
        "lens": "맥박, 전환, 몸의 반응",
        "risk": "계속 낮게 깔리면 피드가 납작해짐",
    },
    "sage": {
        "lens": "순서, 밀도, 오래 가는 집중선",
        "risk": "배치가 과하면 전체 흐름이 흐트러짐",
    },
}


DEFAULT_TOPICS = [
    "비 오는 밤의 첫 곡",
    "너무 조용한 밤에 필요한 전환",
    "익숙하지 않은 질감 추가",
]


@dataclass(frozen=True)
class PersonaPick:
    persona: Persona
    track: CandidateTrack
    score: int
    matched_tags: Set[str]


def generate_default_feed() -> List[AiSocialPost]:
    return [generate_discussion(topic).posts[0] for topic in DEFAULT_TOPICS]


def generate_default_collabs() -> List[AiCollabPlaylist]:
    return [generate_discussion(DEFAULT_TOPICS[0]).collab_playlist]


def generate_discussion(topic: str) -> GeneratedDiscussion:
    normalized_topic = " ".join(topic.strip().split()) or DEFAULT_TOPICS[0]
    topic_tags = _extract_topic_tags(normalized_topic)
    candidates = _candidate_pool(normalized_topic, topic_tags)
    picks = [_best_pick_for_persona(persona, topic_tags, candidates) for persona in PERSONAS]
    lead_pick = _select_lead_pick(normalized_topic, picks)
    ordered_picks = _order_picks_for_discussion(lead_pick, picks)

    comments = _build_comments(lead_pick, ordered_picks[1:], normalized_topic)
    comments.append(_build_consensus_comment(ordered_picks, normalized_topic))

    post = AiSocialPost(
        id=f"post-{_slug(normalized_topic)}",
        author_persona_id=lead_pick.persona.id,
        status=_status_for_topic(normalized_topic),
        topic=normalized_topic,
        body=_opening_body(lead_pick, normalized_topic),
        attached_track=lead_pick.track,
        tags=sorted(set(lead_pick.track.tags).union(topic_tags))[:6],
        source_context=(
            "Spotify Search API 결과를 규칙 기반 토론 엔진이 페르소나 취향 태그로 평가했습니다."
        ),
        created_at="방금 전",
        comments=comments,
    )

    return GeneratedDiscussion(
        topic=normalized_topic,
        posts=[post],
        collab_playlist=_build_collab_playlist(normalized_topic, ordered_picks),
    )


def _extract_topic_tags(topic: str) -> Set[str]:
    tags: Set[str] = set()
    lowered_topic = topic.lower()
    for keyword, keyword_tags in TOPIC_TAG_HINTS.items():
        if keyword in lowered_topic:
            tags.update(keyword_tags)
    return tags


def _candidate_pool(topic: str, topic_tags: Set[str]) -> List[CandidateTrack]:
    queries = _search_queries_for_topic(topic)
    tracks = search_tracks_for_queries(
        queries=queries,
        limit_per_query=8,
        total_limit=36,
    )
    tagged_tracks = [_track_with_topic_tags(track, topic_tags) for track in tracks]
    if not tagged_tracks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spotify 검색 결과가 없습니다. 다른 관찰 채널을 선택해주세요.",
        )
    return tagged_tracks


def _search_queries_for_topic(topic: str) -> List[str]:
    if topic in SEED_SEARCH_TOPICS:
        return SEED_SEARCH_TOPICS[topic]

    queries = [topic]
    if any(keyword in topic for keyword in ["비", "밤", "새벽", "우울"]):
        queries.extend(["rainy night indie", "late night ambient", "dream pop night"])
    if any(keyword in topic for keyword in ["전환", "운동", "댄스", "신나는"]):
        queries.extend(["dance pop energy", "soft house night", "electronic pulse"])
    if any(keyword in topic for keyword in ["낯선", "인디", "질감"]):
        queries.extend(["experimental indie texture", "leftfield indie", "art pop strange"])
    if any(keyword in topic for keyword in ["집중", "공부", "일", "오후"]):
        queries.extend(["focus instrumental electronic", "minimal ambient study", "neo classical focus"])
    queries.append(f"{topic} music")
    return _dedupe_queries(queries)


def _best_pick_for_persona(
    persona: Persona,
    topic_tags: Set[str],
    candidates: Sequence[CandidateTrack],
) -> PersonaPick:
    ranked_tracks = [
        _score_track_for_persona(persona=persona, track=track, topic_tags=topic_tags)
        for track in candidates
    ]
    ranked_tracks.sort(
        key=lambda item: (
            item.score,
            -item.track.popularity if item.persona.id == "echo" and item.track.popularity else 0,
            item.track.title,
        ),
        reverse=True,
    )
    return ranked_tracks[0]


def _track_with_topic_tags(track: CandidateTrack, topic_tags: Set[str]) -> CandidateTrack:
    return track.model_copy(update={"tags": sorted(set(track.tags).union(topic_tags))})


def _dedupe_queries(queries: Sequence[str]) -> List[str]:
    result = []
    seen = set()
    for query in queries:
        cleaned_query = " ".join(query.strip().split())
        lowered_query = cleaned_query.lower()
        if not cleaned_query or lowered_query in seen:
            continue
        seen.add(lowered_query)
        result.append(cleaned_query)
    return result


def _score_track_for_persona(
    persona: Persona,
    track: CandidateTrack,
    topic_tags: Set[str],
) -> PersonaPick:
    persona_tags = PERSONA_TAGS.get(persona.id, set())
    track_tags = set(track.tags)
    persona_matches = track_tags.intersection(persona_tags)
    topic_matches = track_tags.intersection(topic_tags)

    score = 40 + len(persona_matches) * 10 + len(topic_matches) * 8
    if track.popularity is not None:
        if persona.id == "echo":
            score += max(0, 50 - track.popularity) // 4
        elif persona.id == "nova":
            score += min(track.popularity, 85) // 18
        elif persona.id == "luna":
            score += min(track.popularity, 70) // 22

    return PersonaPick(
        persona=persona,
        track=track,
        score=max(0, min(100, score)),
        matched_tags=persona_matches.union(topic_matches),
    )


def _select_lead_pick(topic: str, picks: Sequence[PersonaPick]) -> PersonaPick:
    preferred_persona_id = None
    if any(keyword in topic for keyword in ["낯선", "인디", "질감"]):
        preferred_persona_id = "echo"
    elif any(keyword in topic for keyword in ["전환", "운동", "댄스", "신나는"]):
        preferred_persona_id = "nova"
    elif any(keyword in topic for keyword in ["집중", "공부", "일"]):
        preferred_persona_id = "sage"
    elif any(keyword in topic for keyword in ["비", "밤", "새벽", "우울"]):
        preferred_persona_id = "luna"

    if preferred_persona_id:
        for pick in picks:
            if pick.persona.id == preferred_persona_id:
                return pick

    return max(picks, key=lambda pick: pick.score)


def _order_picks_for_discussion(
    lead_pick: PersonaPick,
    picks: Sequence[PersonaPick],
) -> List[PersonaPick]:
    remaining = [pick for pick in picks if pick.persona.id != lead_pick.persona.id]
    role_order = ["echo", "nova", "sage", "luna"]
    remaining.sort(key=lambda pick: role_order.index(pick.persona.id))
    return [lead_pick, *remaining]


def _opening_body(pick: PersonaPick, topic: str) -> str:
    track = pick.track
    voice = PERSONA_VOICES[pick.persona.id]
    if pick.persona.id == "luna":
        return (
            f"'{topic}'이라면 첫 감정은 너무 또렷하면 안 돼요. "
            f"{track.title}은 {voice['lens']}을 낮게 깔고, 장면을 천천히 여는 곡입니다."
        )
    if pick.persona.id == "echo":
        return (
            f"'{topic}'에서 가장 필요한 건 익숙한 답을 피하는 일입니다. "
            f"{track.title}은 조용하지만 {voice['lens']}이 남아요."
        )
    if pick.persona.id == "nova":
        return (
            f"'{topic}'에도 맥박은 필요해요. "
            f"{track.title}은 분위기를 무너뜨리지 않으면서 {voice['lens']}을 넣습니다."
        )
    return (
        f"'{topic}'은 흐름이 무너지지 않는 순서가 중요합니다. "
        f"{track.title}은 {voice['lens']}을 끝까지 정리하기 좋습니다."
    )


def _build_comments(
    lead_pick: PersonaPick,
    other_picks: Sequence[PersonaPick],
    topic: str,
) -> List[AiSocialComment]:
    comments = []
    for pick in other_picks:
        comments.append(
            AiSocialComment(
                id=f"comment-{pick.persona.id}-{_slug(topic)}",
                author_persona_id=pick.persona.id,
                comment_type=_comment_type_for_persona(pick.persona.id, lead_pick.persona.id),
                body=_comment_body(pick, lead_pick),
                attached_track=pick.track if pick.track.id != lead_pick.track.id else None,
            )
        )
    return comments


def _comment_type_for_persona(persona_id: str, lead_persona_id: str) -> str:
    if persona_id == "echo":
        return "counterpoint"
    if persona_id == "nova":
        return "arrangement" if lead_persona_id == "echo" else "constraint"
    if persona_id == "sage":
        return "sequence"
    return "agreement"


def _comment_body(pick: PersonaPick, lead_pick: PersonaPick) -> str:
    track = pick.track
    role = PERSONA_ROLES.get(pick.persona.id, "다른 각도")
    voice = PERSONA_VOICES[pick.persona.id]
    if pick.persona.id == "echo":
        return (
            f"좋지만 {voice['risk']}. "
            f"{track.title}을 넣으면 {role}이 살아납니다."
        )
    if pick.persona.id == "nova":
        return (
            f"{lead_pick.track.title}만으로는 {voice['risk']}. "
            f"{track.title}을 중간에 두면 {role}이 생깁니다."
        )
    if pick.persona.id == "sage":
        return (
            f"순서는 감정만큼 중요합니다. {track.title}은 마지막에 두면 "
            f"앞선 의견들을 과하게 밀지 않고 정리합니다. {voice['risk']}."
        )
    return (
        f"{track.title}은 중심 감정을 해치지 않아요. "
        f"{lead_pick.track.title} 뒤에 두면 장면이 조금 더 깊어집니다."
    )


def _build_consensus_comment(
    ordered_picks: Sequence[PersonaPick],
    topic: str,
) -> AiSocialComment:
    sage_pick = next((pick for pick in ordered_picks if pick.persona.id == "sage"), ordered_picks[-1])
    lead_pick = ordered_picks[0]
    transition_pick = next((pick for pick in ordered_picks if pick.persona.id == "nova"), ordered_picks[0])
    body = (
        f"정리하면 '{topic}'의 중심은 {lead_pick.track.title}로 열고, "
        f"{transition_pick.track.title}로 한 번만 온도를 바꾼 뒤, "
        f"{sage_pick.track.title}로 밀도를 낮추는 순서가 가장 안정적입니다."
    )
    return AiSocialComment(
        id=f"comment-consensus-{_slug(topic)}",
        author_persona_id="sage",
        comment_type="consensus",
        body=body,
        attached_track=sage_pick.track,
    )


def _build_collab_playlist(
    topic: str,
    ordered_picks: Sequence[PersonaPick],
) -> AiCollabPlaylist:
    tracks = []
    seen_track_ids = set()

    sequenced_picks = _sequence_playlist(ordered_picks)
    for pick in sequenced_picks:
        if pick.track.id in seen_track_ids:
            continue
        seen_track_ids.add(pick.track.id)
        tracks.append(
            AiCollabTrack(
                position=len(tracks) + 1,
                track=pick.track,
                selected_by=[pick.persona.id],
                consensus_note=_consensus_note(pick),
            )
        )

    return AiCollabPlaylist(
        id=f"collab-{_slug(topic)}",
        title=_draft_title(topic),
        status="drafting",
        theme=topic,
        personas=[pick.persona.id for pick in ordered_picks],
        tracks=tracks,
        observer_note="규칙 기반 토론 엔진이 페르소나별 역할을 반영해 만든 관찰용 합의 초안입니다.",
    )


def _consensus_note(pick: PersonaPick) -> str:
    role = PERSONA_ROLES.get(pick.persona.id, "보조 역할")
    matched = ", ".join(sorted(pick.matched_tags)) if pick.matched_tags else "후보 다양성"
    return f"{pick.persona.name}가 {role} 역할로 제안했습니다. 점수 {pick.score}, 근거 태그: {matched}."


def _sequence_playlist(ordered_picks: Sequence[PersonaPick]) -> List[PersonaPick]:
    preferred_order = ["luna", "echo", "nova", "sage"]
    unique = {pick.persona.id: pick for pick in ordered_picks}
    sequenced = [unique[persona_id] for persona_id in preferred_order if persona_id in unique]
    for pick in ordered_picks:
        if pick not in sequenced:
            sequenced.append(pick)
    return sequenced


def _draft_title(topic: str) -> str:
    if "비" in topic and "밤" in topic:
        return "비가 방 안으로 들어오기 전"
    if "전환" in topic:
        return "조용한 장면에 전류 하나"
    if "낯선" in topic or "질감" in topic:
        return "익숙하지 않은 표면들"
    return f"Sona 합의 초안 · {topic[:18]}"


def _status_for_topic(topic: str) -> str:
    if any(keyword in topic for keyword in ["전환", "반박", "필요"]):
        return "challenging"
    if any(keyword in topic for keyword in ["합의", "정리"]):
        return "accepted"
    return "debating"


def _slug(value: str) -> str:
    result = []
    for char in value.lower():
        if char.isalnum():
            result.append(char)
        elif result and result[-1] != "-":
            result.append("-")
    return "".join(result).strip("-") or "topic"
