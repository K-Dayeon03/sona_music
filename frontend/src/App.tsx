import { useEffect, useRef, useState, type FormEvent } from 'react'
import { personas, featuredCollabs, type Persona, type Track } from './data'

type SpotifyStatus = {
  configured: boolean
  connected: boolean
  expires_at: string | null
  scopes: string[]
}

type ApiPersona = {
  id: string
  name: string
  tagline: string
  color: string
}

type ApiTrack = {
  id: string
  title: string
  artist: string
  album: string
  spotify_uri?: string | null
  spotify_url?: string | null
  album_image_url?: string | null
  release_date?: string | null
  popularity?: number | null
  explicit: boolean
  tags: string[]
}

type ApiRecommendation = {
  track: ApiTrack
  persona_id: string
  score: number
  confidence: string
  reasons: string[]
  concerns: string[]
  tags: string[]
}

type ApiPersonaResult = {
  persona: ApiPersona
  recommendations: ApiRecommendation[]
}

type RecommendationResponse = {
  session_id: string
  prompt: string
  candidate_sources: string[]
  persona_results: ApiPersonaResult[]
  playlist_draft: {
    name: string
    description: string
    track_ids: string[]
    default_public: boolean
  }
}

function FeatureBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="font-mono text-[10px] uppercase tracking-widest" style={{ color: 'rgba(255,255,255,0.4)' }}>
          {label}
        </span>
        <span className="font-mono text-[10px]" style={{ color: 'rgba(255,255,255,0.6)' }}>
          {value.toFixed(2)}
        </span>
      </div>
      <div className="feature-bar">
        <div
          className="feature-bar-fill"
          style={{ width: `${value * 100}%`, background: color }}
        />
      </div>
    </div>
  )
}

function WaveIcon() {
  return (
    <div className="flex items-end gap-[2px] h-5">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="wave-bar" style={{ animationDelay: `${(i - 1) * 0.15}s` }} />
      ))}
    </div>
  )
}

function RecommendationResults({ result }: { result: RecommendationResponse }) {
  return (
    <section className="mb-14">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-display font-bold text-xl" style={{ color: '#f0f0f0' }}>
            추천 결과
          </h2>
          <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.38)' }}>
            후보 출처: {result.candidate_sources.join(', ')}
          </p>
        </div>
        <div
          className="font-mono text-[10px] px-2.5 py-1 rounded-full uppercase tracking-wider"
          style={{ background: 'rgba(236,238,129,0.1)', color: '#ECEE81' }}
        >
          {result.playlist_draft.track_ids.length} draft tracks
        </div>
      </div>

      <div className="space-y-5">
        {result.persona_results.map((group) => (
          <div key={group.persona.id}>
            <div className="flex items-center gap-2 mb-3 px-1">
              <div
                className="w-2.5 h-2.5 rounded-full"
                style={{ background: group.persona.color }}
              />
              <div className="font-display font-bold" style={{ color: group.persona.color }}>
                {group.persona.name}
              </div>
              <div className="text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
                {group.persona.tagline}
              </div>
            </div>

            <div
              className="rounded-2xl overflow-hidden"
              style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)' }}
            >
              {group.recommendations.slice(0, 4).map((recommendation, index) => (
                <div
                  key={`${group.persona.id}-${recommendation.track.id}`}
                  className="flex items-center gap-4 px-4 py-3"
                  style={{ borderTop: index === 0 ? 'none' : '1px solid rgba(255,255,255,0.05)' }}
                >
                  <div className="font-mono text-xs w-6" style={{ color: 'rgba(255,255,255,0.28)' }}>
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  <div
                    className="w-12 h-12 rounded-lg flex-shrink-0 bg-white/10"
                    style={{
                      backgroundImage: recommendation.track.album_image_url ? `url(${recommendation.track.album_image_url})` : undefined,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-display font-semibold text-sm truncate" style={{ color: '#f0f0f0' }}>
                      {recommendation.track.title}
                    </div>
                    <div className="text-xs truncate" style={{ color: 'rgba(255,255,255,0.45)' }}>
                      {recommendation.track.artist} · {recommendation.track.album}
                    </div>
                    <div className="text-xs mt-1 line-clamp-2" style={{ color: 'rgba(255,255,255,0.48)' }}>
                      {recommendation.reasons.join(' ')}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <div
                      className="font-mono text-[10px] px-2 py-1 rounded-full"
                      style={{ background: `${group.persona.color}18`, color: group.persona.color }}
                    >
                      {recommendation.score}
                    </div>
                    {recommendation.track.spotify_url && (
                      <a
                        className="font-mono text-[10px] px-2 py-1 rounded-lg transition-all"
                        style={{ background: 'rgba(30,215,96,0.14)', color: '#1ED760' }}
                        href={recommendation.track.spotify_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Spotify
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function TrackRow({
  track,
  index,
  personaColor,
  isPlaying,
  onPlay,
}: {
  track: Track
  index: number
  personaColor: string
  isPlaying: boolean
  onPlay: () => void
}) {
  const [hovered, setHovered] = useState(false)
  const [showWhy, setShowWhy] = useState(false)

  return (
    <>
      <div
        className="group flex items-center gap-4 px-4 py-3 rounded-xl cursor-pointer transition-all duration-200"
        style={{ background: hovered ? 'rgba(255,255,255,0.05)' : 'transparent' }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={onPlay}
      >
        <div className="w-6 flex-shrink-0 flex items-center justify-center">
          {isPlaying ? (
            <WaveIcon />
          ) : (
            <span
              className="font-mono text-sm transition-all"
              style={{ color: hovered ? '#ECEE81' : 'rgba(255,255,255,0.3)' }}
            >
              {hovered ? '▶' : String(index + 1).padStart(2, '0')}
            </span>
          )}
        </div>

        <div
          className="w-10 h-10 rounded-lg flex-shrink-0 bg-white/10"
          style={{
            backgroundImage: `url(https://images.unsplash.com/${track.imgId}?w=80&h=80&fit=crop&auto=format)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        <div className="flex-1 min-w-0">
          <div
            className="font-display font-semibold text-sm truncate"
            style={{ color: isPlaying ? personaColor : '#f0f0f0' }}
          >
            {track.title}
          </div>
          <div className="text-xs truncate" style={{ color: 'rgba(255,255,255,0.45)' }}>
            {track.artist} · {track.album}
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <button
            className="text-[10px] px-2 py-1 rounded-full transition-all duration-200"
            style={{
              background: showWhy ? personaColor : 'rgba(255,255,255,0.08)',
              color: showWhy ? '#0c0c0e' : 'rgba(255,255,255,0.5)',
              fontFamily: 'var(--font-mono)',
            }}
            onClick={(e) => {
              e.stopPropagation()
              setShowWhy(!showWhy)
            }}
          >
            WHY?
          </button>

          <div className="hidden sm:flex items-center gap-3">
            <span
              className="font-mono text-[10px] px-1.5 py-0.5 rounded"
              style={{ background: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.4)' }}
            >
              {track.tempo} BPM
            </span>
          </div>

          <span className="font-mono text-xs" style={{ color: 'rgba(255,255,255,0.3)' }}>
            {track.duration}
          </span>
        </div>
      </div>

      {showWhy && (
        <div
          className="mx-14 mb-2 px-4 py-3 rounded-xl text-sm"
          style={{
            background: `${personaColor}15`,
            borderLeft: `2px solid ${personaColor}`,
            color: 'rgba(255,255,255,0.7)',
            fontStyle: 'italic',
          }}
        >
          "{track.why}"
        </div>
      )}
    </>
  )
}

function PersonaCard({
  persona,
  onClick,
  isActive,
}: {
  persona: Persona
  onClick: () => void
  isActive: boolean
}) {
  return (
    <button
      className="relative text-left rounded-2xl p-6 transition-all duration-300 cursor-pointer w-full"
      style={{
        background: isActive ? `${persona.color}18` : 'rgba(255,255,255,0.03)',
        border: isActive ? `1.5px solid ${persona.color}60` : '1.5px solid rgba(255,255,255,0.07)',
        transform: isActive ? 'translateY(-2px)' : 'translateY(0)',
      }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0"
          style={{ background: `${persona.color}25` }}
        >
          {persona.emoji}
        </div>
        {isActive && (
          <div
            className="font-mono text-[9px] px-2 py-1 rounded-full uppercase tracking-wider"
            style={{ background: persona.color, color: '#0c0c0e' }}
          >
            선택됨
          </div>
        )}
      </div>

      <div className="font-display font-bold text-xl mb-0.5" style={{ color: persona.color }}>
        {persona.name}
      </div>
      <div className="text-xs mb-3" style={{ color: 'rgba(255,255,255,0.45)' }}>
        {persona.tagline}
      </div>

      <div className="flex flex-wrap gap-1 mb-4">
        {persona.preferredGenres.slice(0, 2).map((g) => (
          <span
            key={g}
            className="font-mono text-[9px] px-2 py-0.5 rounded-full uppercase tracking-wider"
            style={{ background: `${persona.color}18`, color: persona.color }}
          >
            {g}
          </span>
        ))}
      </div>

      <div className="space-y-2">
        {persona.traits.slice(0, 2).map((t) => (
          <FeatureBar key={t.label} label={t.label} value={t.value} color={persona.color} />
        ))}
      </div>

      <div
        className="mt-4 pt-3 flex items-center justify-between"
        style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
      >
        <span className="text-[11px]" style={{ color: 'rgba(255,255,255,0.35)' }}>
          {persona.followers.toLocaleString()} followers
        </span>
        <span
          className="font-mono text-[10px] px-2 py-0.5 rounded"
          style={{ background: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.4)' }}
        >
          {persona.playlist.length} tracks
        </span>
      </div>
    </button>
  )
}

function PersonaDetail({
  persona,
  playingId,
  onPlay,
}: {
  persona: Persona
  playingId: string | null
  onPlay: (id: string) => void
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div
        className="rounded-2xl p-6 relative overflow-hidden"
        style={{ background: `${persona.color}10`, border: `1px solid ${persona.color}25` }}
      >
        <div
          className="absolute inset-0 opacity-5"
          style={{
            background: `radial-gradient(circle at 80% 50%, ${persona.color} 0%, transparent 60%)`,
          }}
        />
        <div className="relative flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl flex-shrink-0"
            style={{ background: `${persona.color}20` }}
          >
            {persona.emoji}
          </div>
          <div className="flex-1">
            <div className="font-display font-black text-3xl" style={{ color: persona.color }}>
              {persona.name}
            </div>
            <div className="text-sm mt-1 mb-3 max-w-lg" style={{ color: 'rgba(255,255,255,0.55)' }}>
              {persona.bio}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {persona.preferredGenres.map((g) => (
                <span
                  key={g}
                  className="font-mono text-[9px] px-2.5 py-1 rounded-full uppercase tracking-wider"
                  style={{ background: `${persona.color}18`, color: persona.color }}
                >
                  {g}
                </span>
              ))}
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <div
              className="font-mono text-[10px] uppercase tracking-wider mb-1"
              style={{ color: 'rgba(255,255,255,0.35)' }}
            >
              지금 큐레이팅 중
            </div>
            <div className="font-display font-semibold text-sm" style={{ color: persona.color }}>
              {persona.curatingNow}
            </div>
          </div>
        </div>
      </div>

      {/* Audio Profile */}
      <div
        className="rounded-2xl p-5"
        style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
      >
        <div
          className="font-mono text-[10px] uppercase tracking-widest mb-4"
          style={{ color: 'rgba(255,255,255,0.3)' }}
        >
          Audio DNA
        </div>
        <div className="grid grid-cols-2 gap-4">
          {persona.traits.map((t) => (
            <FeatureBar key={t.label} label={t.label} value={t.value} color={persona.color} />
          ))}
        </div>
      </div>

      {/* Playlist */}
      <div>
        <div
          className="font-mono text-[10px] uppercase tracking-widest mb-3 px-1"
          style={{ color: 'rgba(255,255,255,0.3)' }}
        >
          Curated Playlist · {persona.playlist.length} tracks
        </div>
        <div className="space-y-0.5">
          {persona.playlist.map((track, i) => (
            <TrackRow
              key={track.id}
              track={track}
              index={i}
              personaColor={persona.color}
              isPlaying={playingId === track.id}
              onPlay={() => onPlay(track.id)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function NowPlayingBar({
  track,
  persona,
  onClose,
}: {
  track: Track
  persona: Persona
  onClose: () => void
}) {
  const [progress, setProgress] = useState(34)

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50 px-4 pb-4"
    >
      <div
        className="max-w-3xl mx-auto rounded-2xl px-5 py-4 flex items-center gap-4"
        style={{
          background: 'rgba(18,18,20,0.95)',
          backdropFilter: 'blur(20px)',
          border: `1px solid ${persona.color}30`,
        }}
      >
        <div
          className="w-10 h-10 rounded-lg flex-shrink-0"
          style={{
            backgroundImage: `url(https://images.unsplash.com/${track.imgId}?w=80&h=80&fit=crop&auto=format)`,
            backgroundSize: 'cover',
          }}
        />
        <div className="flex-1 min-w-0">
          <div className="font-display font-semibold text-sm truncate" style={{ color: persona.color }}>
            {track.title}
          </div>
          <div className="text-xs truncate" style={{ color: 'rgba(255,255,255,0.4)' }}>
            {track.artist}
          </div>
          <div className="mt-2 feature-bar cursor-pointer" onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect()
            setProgress(Math.round(((e.clientX - rect.left) / rect.width) * 100))
          }}>
            <div className="feature-bar-fill" style={{ width: `${progress}%`, background: persona.color }} />
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <WaveIcon />
          <div
            className="flex items-center gap-1.5 font-mono text-[10px]"
            style={{ color: 'rgba(255,255,255,0.35)' }}
          >
            <span>{persona.emoji}</span>
            <span>{persona.name}</span>
          </div>
          <button
            className="w-7 h-7 flex items-center justify-center rounded-full transition-all"
            style={{ background: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.5)' }}
            onClick={onClose}
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [activePersonaId, setActivePersonaId] = useState<string>('luna')
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [view, setView] = useState<'home' | 'explore'>('home')
  const [prompt, setPrompt] = useState('비 오는 밤에 들을 곡')
  const [spotifyStatus, setSpotifyStatus] = useState<SpotifyStatus | null>(null)
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null)
  const [recommendationError, setRecommendationError] = useState<string | null>(null)
  const [isRecommending, setIsRecommending] = useState(false)
  const detailRef = useRef<HTMLDivElement>(null)

  const activePersona = personas.find((p) => p.id === activePersonaId)!
  const playingTrack = activePersona?.playlist.find((t) => t.id === playingId) ?? null

  const handleSelectPersona = (id: string) => {
    setActivePersonaId(id)
    setPlayingId(null)
    setTimeout(() => {
      detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }

  const handlePlay = (id: string) => {
    setPlayingId((prev) => (prev === id ? null : id))
  }

  useEffect(() => {
    fetch('/api/auth/spotify/status')
      .then((response) => response.json())
      .then((data: SpotifyStatus) => setSpotifyStatus(data))
      .catch(() => setSpotifyStatus(null))
  }, [])

  const handleCreateRecommendations = async (event: FormEvent) => {
    event.preventDefault()
    setIsRecommending(true)
    setRecommendationError(null)

    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          candidate_sources: ['saved_tracks', 'search'],
          limit: 8,
        }),
      })

      if (!response.ok) {
        throw new Error(`추천 요청 실패 (${response.status})`)
      }

      const data = (await response.json()) as RecommendationResponse
      setRecommendation(data)
    } catch (error) {
      setRecommendationError(error instanceof Error ? error.message : '추천을 가져오지 못했습니다.')
    } finally {
      setIsRecommending(false)
    }
  }

  return (
    <div style={{ background: '#0c0c0e', minHeight: '100vh' }}>
      {/* Nav */}
      <header
        className="sticky top-0 z-40 px-6 py-4"
        style={{ background: 'rgba(12,12,14,0.85)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
              style={{ background: '#ECEE81' }}
            >
              🎵
            </div>
            <span className="font-display font-bold text-lg tracking-tight" style={{ color: '#ECEE81' }}>
              sona
            </span>
          </div>

          <nav className="flex items-center gap-1">
            {[
              { id: 'home', label: 'Home' },
              { id: 'explore', label: 'Explore' },
            ].map((item) => (
              <button
                key={item.id}
                className="font-display text-sm px-4 py-1.5 rounded-lg transition-all duration-200"
                style={{
                  background: view === item.id ? 'rgba(236,238,129,0.12)' : 'transparent',
                  color: view === item.id ? '#ECEE81' : 'rgba(255,255,255,0.45)',
                }}
                onClick={() => setView(item.id as typeof view)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 pt-10 pb-32">
        {view === 'home' && (
          <>
            {/* Hero */}
            <section className="mb-14 text-center">
              <div
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-6 font-mono text-[10px] uppercase tracking-widest"
                style={{ background: 'rgba(236,238,129,0.1)', color: '#ECEE81', border: '1px solid rgba(236,238,129,0.2)' }}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                4 AI 에이전트 운영 중
              </div>

              <h1
                className="font-display font-black leading-[1.05] mb-5"
                style={{ fontSize: 'clamp(2.2rem, 6vw, 3.8rem)', color: '#f0f0f0' }}
              >
                음악을 고르는
                <br />
                <span style={{ color: '#ECEE81' }}>AI 친구들</span>을 만나세요
              </h1>

              <p
                className="text-base max-w-md mx-auto leading-relaxed"
                style={{ color: 'rgba(255,255,255,0.45)' }}
              >
                각자의 음악 취향과 성격을 가진 AI 페르소나들이 Spotify 후보곡과
                사용자 맥락을 바탕으로 플레이리스트 초안을 큐레이션합니다.
              </p>

              <form
                className="mt-8 max-w-xl mx-auto"
                onSubmit={handleCreateRecommendations}
              >
                <div
                  className="flex flex-col sm:flex-row gap-2 rounded-2xl p-2"
                  style={{ background: 'rgba(255,255,255,0.045)', border: '1px solid rgba(255,255,255,0.08)' }}
                >
                  <input
                    className="flex-1 bg-transparent px-4 py-3 text-sm outline-none"
                    style={{ color: '#f0f0f0' }}
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    placeholder="비 오는 밤에 들을 곡"
                  />
                  <button
                    className="font-display font-semibold px-5 py-3 rounded-xl text-sm transition-all duration-200 active:scale-95"
                    style={{ background: '#ECEE81', color: '#0c0c0e' }}
                    type="submit"
                    disabled={isRecommending}
                  >
                    {isRecommending ? '추천 중' : '추천 받기'}
                  </button>
                </div>
                <div className="mt-3 flex flex-col sm:flex-row items-center justify-center gap-2">
                  <button
                    className="font-display font-medium px-4 py-2 rounded-xl text-xs transition-all duration-200"
                    style={{
                      background: spotifyStatus?.connected ? 'rgba(30,215,96,0.12)' : 'rgba(255,255,255,0.06)',
                      color: spotifyStatus?.connected ? '#1ED760' : 'rgba(255,255,255,0.65)',
                      border: spotifyStatus?.connected ? '1px solid rgba(30,215,96,0.24)' : '1px solid rgba(255,255,255,0.08)',
                    }}
                    type="button"
                    onClick={() => {
                      window.location.href = '/api/auth/spotify/login'
                    }}
                  >
                    {spotifyStatus?.connected ? 'Spotify 연결됨' : 'Spotify 연결'}
                  </button>
                  {recommendationError && (
                    <span className="text-xs" style={{ color: '#f5a9c0' }}>
                      {recommendationError}
                    </span>
                  )}
                </div>
              </form>
            </section>

            {recommendation && <RecommendationResults result={recommendation} />}

            {/* Stats row */}
            <div
              className="grid grid-cols-3 gap-3 mb-14 rounded-2xl p-5"
              style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)' }}
            >
              {[
                { value: '4', label: 'AI 페르소나' },
                { value: '95.6K', label: '총 팔로워' },
                { value: '1,240+', label: '큐레이팅된 트랙' },
              ].map((s) => (
                <div key={s.label} className="text-center">
                  <div className="font-display font-black text-2xl" style={{ color: '#ECEE81' }}>
                    {s.value}
                  </div>
                  <div className="font-mono text-[10px] uppercase tracking-wider mt-1" style={{ color: 'rgba(255,255,255,0.3)' }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>

            {/* Personas grid */}
            <section id="personas" className="mb-14">
              <div className="flex items-center justify-between mb-5">
                <h2 className="font-display font-bold text-xl" style={{ color: '#f0f0f0' }}>
                  AI 페르소나
                </h2>
                <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.25)' }}>
                  클릭해서 탐색
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {personas.map((p) => (
                  <PersonaCard
                    key={p.id}
                    persona={p}
                    isActive={activePersonaId === p.id}
                    onClick={() => handleSelectPersona(p.id)}
                  />
                ))}
              </div>
            </section>

            {/* Detail */}
            <section ref={detailRef}>
              <PersonaDetail
                persona={activePersona}
                playingId={playingId}
                onPlay={handlePlay}
              />
            </section>

            {/* Collabs */}
            <section className="mt-14">
              <h2 className="font-display font-bold text-xl mb-5" style={{ color: '#f0f0f0' }}>
                AI 협업 플레이리스트
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {featuredCollabs.map((c) => {
                  const p1 = personas.find((p) => p.id === c.personas[0])!
                  const p2 = personas.find((p) => p.id === c.personas[1])!
                  return (
                    <div
                      key={c.id}
                      className="relative rounded-2xl overflow-hidden cursor-pointer group"
                      style={{ border: '1px solid rgba(255,255,255,0.07)' }}
                    >
                      <div
                        className="absolute inset-0"
                        style={{
                          backgroundImage: `url(https://images.unsplash.com/${c.imgId}?w=600&h=300&fit=crop&auto=format)`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          filter: 'brightness(0.25)',
                          transition: 'filter 0.3s',
                        }}
                      />
                      <div
                        className="absolute inset-0 opacity-60"
                        style={{
                          background: `linear-gradient(135deg, ${p1.color}40, ${p2.color}40)`,
                        }}
                      />
                      <div className="relative p-5">
                        <div className="flex items-center gap-2 mb-3">
                          {[p1, p2].map((p) => (
                            <div
                              key={p.id}
                              className="w-8 h-8 rounded-xl flex items-center justify-center text-base"
                              style={{ background: `${p.color}25`, border: `1px solid ${p.color}40` }}
                            >
                              {p.emoji}
                            </div>
                          ))}
                          <span
                            className="font-mono text-[10px] ml-1 uppercase tracking-wider"
                            style={{ color: 'rgba(255,255,255,0.4)' }}
                          >
                            {c.trackCount} tracks
                          </span>
                        </div>
                        <div className="font-display font-bold text-base" style={{ color: '#f0f0f0' }}>
                          {c.title}
                        </div>
                        <div className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.5)' }}>
                          {c.description}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          </>
        )}

        {view === 'explore' && (
          <section>
            <div className="mb-8">
              <h2 className="font-display font-black text-3xl mb-2" style={{ color: '#f0f0f0' }}>
                전체 탐색
              </h2>
              <p className="text-sm" style={{ color: 'rgba(255,255,255,0.4)' }}>
                모든 AI의 플레이리스트를 한 곳에서
              </p>
            </div>

            <div className="space-y-8">
              {personas.map((persona) => (
                <div key={persona.id}>
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
                      style={{ background: `${persona.color}20` }}
                    >
                      {persona.emoji}
                    </div>
                    <div>
                      <div className="font-display font-bold" style={{ color: persona.color }}>
                        {persona.name}
                      </div>
                      <div className="text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
                        {persona.tagline}
                      </div>
                    </div>
                    <button
                      className="ml-auto font-mono text-[10px] px-3 py-1.5 rounded-lg transition-all"
                      style={{ background: `${persona.color}18`, color: persona.color, border: `1px solid ${persona.color}30` }}
                      onClick={() => {
                        setActivePersonaId(persona.id)
                        setView('home')
                        setTimeout(() => document.getElementById('personas')?.scrollIntoView({ behavior: 'smooth' }), 100)
                      }}
                    >
                      전체 보기
                    </button>
                  </div>

                  <div className="space-y-0.5 rounded-2xl overflow-hidden" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    {persona.playlist.slice(0, 3).map((track, i) => (
                      <TrackRow
                        key={track.id}
                        track={track}
                        index={i}
                        personaColor={persona.color}
                        isPlaying={playingId === track.id}
                        onPlay={() => {
                          setActivePersonaId(persona.id)
                          handlePlay(track.id)
                        }}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Now Playing */}
      {playingTrack && (
        <NowPlayingBar
          track={playingTrack}
          persona={activePersona}
          onClose={() => setPlayingId(null)}
        />
      )}
    </div>
  )
}
