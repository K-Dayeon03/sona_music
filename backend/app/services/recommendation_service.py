from typing import Iterable, List, Optional, Set
from uuid import uuid4

from app.data.seed import PERSONAS
from app.models.schemas import (
    CandidateTrack,
    Persona,
    PersonaRecommendationGroup,
    PlaylistDraft,
    RecommendationRequest,
    RecommendationResponse,
    TrackRecommendation,
)
from app.services.spotify_catalog_service import search_tracks_for_queries


PROMPT_TAG_HINTS = {
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


async def create_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    candidates, actual_sources = await _collect_candidates(request)
    selected_personas = _select_personas(request.persona_ids)
    prompt_tags = _extract_prompt_tags(request.prompt)

    groups = [
        PersonaRecommendationGroup(
            persona=persona,
            recommendations=_rank_tracks_for_persona(
                persona=persona,
                prompt_tags=prompt_tags,
                candidates=candidates,
                limit=request.limit,
            ),
        )
        for persona in selected_personas
    ]

    draft_track_ids = _collect_playlist_track_ids(groups, request.limit)

    return RecommendationResponse(
        session_id=str(uuid4()),
        prompt=request.prompt,
        candidate_sources=actual_sources,
        persona_results=groups,
        playlist_draft=PlaylistDraft(
            name=_draft_name(request.prompt),
            description="사용자 승인 전까지 Spotify에는 아무 작업도 실행하지 않는 추천 초안입니다.",
            track_ids=draft_track_ids,
            default_public=False,
        ),
    )

async def _collect_candidates(
    request: RecommendationRequest,
) -> tuple[List[CandidateTrack], List[str]]:
    prompt_tags = _extract_prompt_tags(request.prompt)
    queries = _search_queries_for_prompt(request.prompt)
    tracks = search_tracks_for_queries(
        queries=queries,
        limit_per_query=max(6, min(request.limit, 12)),
        total_limit=max(request.limit * 4, 24),
    )
    return [_track_with_prompt_tags(track, prompt_tags) for track in tracks], ["spotify_search"]


def _select_personas(persona_ids: Optional[List[str]]) -> List[Persona]:
    if not persona_ids:
        return PERSONAS

    requested = set(persona_ids)
    return [persona for persona in PERSONAS if persona.id in requested]


def _extract_prompt_tags(prompt: str) -> Set[str]:
    tags: Set[str] = set()
    normalized_prompt = prompt.lower()

    for keyword, keyword_tags in PROMPT_TAG_HINTS.items():
        if keyword in normalized_prompt:
            tags.update(keyword_tags)

    return tags


def _search_queries_for_prompt(prompt: str) -> List[str]:
    queries = [prompt]
    if any(keyword in prompt for keyword in ["비", "밤", "새벽", "우울"]):
        queries.extend(["rainy night indie", "late night ambient", "dream pop night"])
    if any(keyword in prompt for keyword in ["전환", "운동", "댄스", "신나는"]):
        queries.extend(["dance pop energy", "soft house night", "electronic pulse"])
    if any(keyword in prompt for keyword in ["낯선", "인디", "질감"]):
        queries.extend(["experimental indie texture", "leftfield indie", "art pop strange"])
    if any(keyword in prompt for keyword in ["집중", "공부", "일", "오후"]):
        queries.extend(["focus instrumental electronic", "minimal ambient study", "neo classical focus"])
    queries.append(f"{prompt} music")
    return _dedupe_queries(queries)


def _dedupe_queries(queries: Iterable[str]) -> List[str]:
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


def _rank_tracks_for_persona(
    persona: Persona,
    prompt_tags: Set[str],
    candidates: List[CandidateTrack],
    limit: int,
) -> List[TrackRecommendation]:
    scored_tracks = [
        _score_track(persona=persona, track=track, prompt_tags=prompt_tags)
        for track in candidates
    ]
    scored_tracks.sort(key=lambda item: item.score, reverse=True)
    return scored_tracks[:limit]


def _score_track(
    persona: Persona,
    track: CandidateTrack,
    prompt_tags: Set[str],
) -> TrackRecommendation:
    persona_tags = PERSONA_TAGS.get(persona.id, set())
    track_tags = set(track.tags)
    persona_matches = track_tags.intersection(persona_tags)
    prompt_matches = track_tags.intersection(prompt_tags)

    score = 45 + len(persona_matches) * 9 + len(prompt_matches) * 7
    if track.popularity is not None:
        if persona.id == "echo":
            score += max(0, 50 - track.popularity) // 5
        elif persona.id in {"nova", "luna"}:
            score += min(track.popularity, 80) // 20

    score = max(0, min(100, score))
    confidence = _confidence(score, prompt_matches)

    return TrackRecommendation(
        track=track,
        persona_id=persona.id,
        score=score,
        confidence=confidence,
        reasons=_reasons(persona, track, persona_matches, prompt_matches),
        concerns=_concerns(persona, track),
        tags=sorted(track_tags.union(prompt_matches)),
    )


def _confidence(score: int, prompt_matches: Set[str]) -> str:
    if score >= 80 and prompt_matches:
        return "high"
    if score >= 62:
        return "medium"
    return "low"


def _reasons(
    persona: Persona,
    track: CandidateTrack,
    persona_matches: Set[str],
    prompt_matches: Set[str],
) -> List[str]:
    reasons = []
    if prompt_matches:
        reasons.append(
            "요청 맥락과 맞는 태그가 감지되었습니다: " + ", ".join(sorted(prompt_matches)) + "."
        )
    if persona_matches:
        reasons.append(
            f"{persona.name}의 취향 태그와 겹칩니다: "
            + ", ".join(sorted(persona_matches))
            + "."
        )
    if not reasons:
        reasons.append(f"{track.artist}의 곡 분위기가 후보 다양성을 보완합니다.")

    return reasons[:2]


def _concerns(persona: Persona, track: CandidateTrack) -> List[str]:
    track_tags = set(track.tags)
    avoid_matches = track_tags.intersection(set(persona.avoid_tags))
    if avoid_matches:
        return ["페르소나의 회피 태그와 일부 겹칩니다: " + ", ".join(sorted(avoid_matches)) + "."]
    return []


def _collect_playlist_track_ids(
    groups: Iterable[PersonaRecommendationGroup],
    limit: int,
) -> List[str]:
    result = []
    seen = set()

    for group in groups:
        for recommendation in group.recommendations:
            track_id = recommendation.track.id
            if track_id in seen:
                continue
            seen.add(track_id)
            result.append(track_id)
            if len(result) >= limit:
                return result

    return result


def _draft_name(prompt: str) -> str:
    cleaned = " ".join(prompt.strip().split())
    if len(cleaned) > 24:
        cleaned = cleaned[:24].rstrip() + "..."
    return f"Sona 추천 - {cleaned}"


def _track_with_prompt_tags(track: CandidateTrack, prompt_tags: Set[str]) -> CandidateTrack:
    return track.model_copy(update={"tags": sorted(set(track.tags).union(prompt_tags))})
