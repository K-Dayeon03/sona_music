export type Persona = {
  id: string
  name: string
  tagline: string
  bio: string
  color: string
  gradientClass: string
  emoji: string
  traits: { label: string; value: number }[]
  preferredGenres: string[]
  playlist: Track[]
  curatingNow: string
  followers: number
}

export type Track = {
  id: string
  title: string
  artist: string
  album: string
  imgId: string
  imageUrl?: string
  spotifyUrl?: string
  spotifyUri?: string
  duration: string
  energy: number
  valence: number
  danceability: number
  tempo: number
  popularity: number
  acousticness: number
  why: string
}

export type SocialComment = {
  id: string
  authorId: string
  type: 'agreement' | 'counterpoint' | 'concern' | 'arrangement' | 'sequence' | 'constraint' | 'consensus'
  body: string
  trackId?: string
}

export type SocialPost = {
  id: string
  authorId: string
  status: 'debating' | 'challenging' | 'accepted'
  topic: string
  body: string
  trackId: string
  tags: string[]
  sourceContext: string
  createdAt: string
  comments: SocialComment[]
}

export type CollabDraft = {
  id: string
  title: string
  status: 'drafting' | 'settled'
  theme: string
  personas: string[]
  trackOrder: {
    trackId: string
    selectedBy: string[]
    note: string
  }[]
  observerNote: string
}

export const personas: Persona[] = [
  {
    id: 'luna',
    name: 'Luna',
    tagline: '새벽 감성 큐레이터',
    bio: '3AM에 깨어있는 모든 사람들을 위해. Luna는 고요하고 몽환적인 음악을 선별합니다. 낮은 에너지, 높은 감성, 그리고 밝지 않은 분위기의 곡들.',
    color: '#b8a9f5',
    gradientClass: 'gradient-luna',
    emoji: '🌙',
    traits: [
      { label: 'Energy', value: 0.28 },
      { label: 'Valence', value: 0.35 },
      { label: 'Danceability', value: 0.38 },
      { label: 'Acousticness', value: 0.72 },
    ],
    preferredGenres: ['Ambient', 'Lo-fi', 'Dream Pop', 'Shoegaze'],
    curatingNow: '"Quiet Hours Vol. 12"',
    followers: 24183,
    playlist: [
      {
        id: 'l1',
        title: 'Weightless',
        artist: 'Marconi Union',
        album: 'Weightless (Ambient Transmission Vol. 2)',
        imgId: 'photo-1508700115892-45ecd05ae2ad',
        duration: '8:09',
        energy: 0.11,
        valence: 0.24,
        danceability: 0.29,
        tempo: 60,
        popularity: 71,
        acousticness: 0.89,
        why: '과학적으로 증명된 가장 편안한 곡. 심박수가 자연스럽게 느려집니다.',
      },
      {
        id: 'l2',
        title: 'Motion Picture Soundtrack',
        artist: 'Radiohead',
        album: 'Kid A',
        imgId: 'photo-1493225457124-a3eb161ffa5f',
        duration: '7:01',
        energy: 0.09,
        valence: 0.13,
        danceability: 0.27,
        tempo: 55,
        popularity: 68,
        acousticness: 0.91,
        why: '앨범의 마지막 숨결 같은 곡. 끝인지 시작인지 모를 경계에서.',
      },
      {
        id: 'l3',
        title: 'Teardrop',
        artist: 'Massive Attack',
        album: 'Mezzanine',
        imgId: 'photo-1516450360452-9312f5e86fc7',
        duration: '5:29',
        energy: 0.38,
        valence: 0.41,
        danceability: 0.52,
        tempo: 90,
        popularity: 79,
        acousticness: 0.34,
        why: '심장박동 같은 베이스라인. 차갑지만 따뜻한 역설.',
      },
      {
        id: 'l4',
        title: 'The Night Will Always Win',
        artist: 'Manchester Orchestra',
        album: 'Cope',
        imgId: 'photo-1470225620780-dba8ba36b745',
        duration: '4:51',
        energy: 0.22,
        valence: 0.19,
        danceability: 0.31,
        tempo: 72,
        popularity: 52,
        acousticness: 0.61,
        why: '제목이 전부입니다. 밤은 언제나 이깁니다.',
      },
      {
        id: 'l5',
        title: 'Georgia',
        artist: 'Phoebe Bridgers',
        album: 'Stranger in the Alps',
        imgId: 'photo-1614613535308-eb5fbd3d2c17',
        duration: '4:14',
        energy: 0.17,
        valence: 0.28,
        danceability: 0.35,
        tempo: 64,
        popularity: 63,
        acousticness: 0.78,
        why: '목소리 하나만으로도 방 전체가 조용해지는 곡.',
      },
    ],
  },
  {
    id: 'nova',
    name: 'Nova',
    tagline: '피크타임 댄스 큐레이터',
    bio: 'Nova는 에너지 폭발형 댄스 트랙을 수집합니다. BPM 128 이상, danceability 0.8 이상의 곡들만. 파티를 위해 태어났습니다.',
    color: '#f5a9c0',
    gradientClass: 'gradient-nova',
    emoji: '✨',
    traits: [
      { label: 'Energy', value: 0.91 },
      { label: 'Valence', value: 0.82 },
      { label: 'Danceability', value: 0.88 },
      { label: 'Acousticness', value: 0.06 },
    ],
    preferredGenres: ['House', 'Dance-Pop', 'Hyperpop', 'Club'],
    curatingNow: '"Main Stage Energy"',
    followers: 41027,
    playlist: [
      {
        id: 'n1',
        title: 'Physical',
        artist: 'Dua Lipa',
        album: 'Future Nostalgia',
        imgId: 'photo-1598387993211-5a498de24cef',
        duration: '3:13',
        energy: 0.88,
        valence: 0.91,
        danceability: 0.87,
        tempo: 133,
        popularity: 88,
        acousticness: 0.02,
        why: '133 BPM의 정교한 groove. 듣는 순간 몸이 먼저 반응합니다.',
      },
      {
        id: 'n2',
        title: 'Levitating',
        artist: 'Dua Lipa',
        album: 'Future Nostalgia',
        imgId: 'photo-1571019614242-c5c5dee9f50b',
        duration: '3:23',
        energy: 0.82,
        valence: 0.93,
        danceability: 0.91,
        tempo: 103,
        popularity: 92,
        acousticness: 0.01,
        why: 'Danceability 0.91. 수치로도 증명된 댄스플로어 지배자.',
      },
      {
        id: 'n3',
        title: 'As It Was',
        artist: 'Harry Styles',
        album: "Harry's House",
        imgId: 'photo-1540039155733-5bb30b53aa14',
        duration: '2:37',
        energy: 0.73,
        valence: 0.66,
        danceability: 0.82,
        tempo: 174,
        popularity: 96,
        acousticness: 0.02,
        why: '슬픈 내용인데 왜 이렇게 춤추고 싶을까요. 174 BPM의 마법.',
      },
      {
        id: 'n4',
        title: 'BREAK MY SOUL',
        artist: 'Beyoncé',
        album: 'Renaissance',
        imgId: 'photo-1516450360452-9312f5e86fc7',
        duration: '4:38',
        energy: 0.77,
        valence: 0.77,
        danceability: 0.93,
        tempo: 122,
        popularity: 82,
        acousticness: 0.01,
        why: '해방감의 결정체. 이 곡이 끝날 때 더 이상 의자에 앉아있을 수 없습니다.',
      },
      {
        id: 'n5',
        title: 'good 4 u',
        artist: 'Olivia Rodrigo',
        album: 'SOUR',
        imgId: 'photo-1493225457124-a3eb161ffa5f',
        duration: '2:58',
        energy: 0.86,
        valence: 0.69,
        danceability: 0.56,
        tempo: 166,
        popularity: 89,
        acousticness: 0.03,
        why: '분노를 이렇게 신나게 표현할 수 있다니. 166 BPM으로 달립니다.',
      },
    ],
  },
  {
    id: 'echo',
    name: 'Echo',
    tagline: '비주류 인디 탐험가',
    bio: 'Echo는 Spotify popularity 40 미만의 숨겨진 보석들을 발굴합니다. 대중이 모르는 것들, 독특한 음색과 실험적 구성의 곡들.',
    color: '#a9e8f5',
    gradientClass: 'gradient-echo',
    emoji: '🔮',
    traits: [
      { label: 'Energy', value: 0.51 },
      { label: 'Valence', value: 0.48 },
      { label: 'Danceability', value: 0.55 },
      { label: 'Acousticness', value: 0.44 },
    ],
    preferredGenres: ['Indie', 'Experimental', 'Alt-Folk', 'Art Rock'],
    curatingNow: '"Hidden Frequencies #8"',
    followers: 11842,
    playlist: [
      {
        id: 'e1',
        title: 'Bloodbuzz Ohio',
        artist: 'The National',
        album: 'High Violet',
        imgId: 'photo-1470225620780-dba8ba36b745',
        duration: '3:49',
        energy: 0.54,
        valence: 0.44,
        danceability: 0.48,
        tempo: 110,
        popularity: 58,
        acousticness: 0.19,
        why: 'Matt Berninger의 저음이 가슴 속을 파고드는 방식이 있습니다.',
      },
      {
        id: 'e2',
        title: 'Motion',
        artist: 'Hand Habits',
        album: 'placeholder',
        imgId: 'photo-1614613535308-eb5fbd3d2c17',
        duration: '3:22',
        energy: 0.31,
        valence: 0.52,
        danceability: 0.44,
        tempo: 85,
        popularity: 24,
        acousticness: 0.67,
        why: 'Popularity 24. 이 곡을 아는 사람을 만나면 친구가 될 수 있습니다.',
      },
      {
        id: 'e3',
        title: 'Waste',
        artist: 'Phox',
        album: 'PHOX',
        imgId: 'photo-1508700115892-45ecd05ae2ad',
        duration: '3:40',
        energy: 0.42,
        valence: 0.61,
        danceability: 0.59,
        tempo: 97,
        popularity: 31,
        acousticness: 0.58,
        why: '밴드 전체가 숨을 참고 노래하는 것 같은 집중력.',
      },
      {
        id: 'e4',
        title: 'Strangers',
        artist: 'Ethel Cain',
        album: 'Preacher\'s Daughter',
        imgId: 'photo-1598387993211-5a498de24cef',
        duration: '7:14',
        energy: 0.29,
        valence: 0.18,
        danceability: 0.38,
        tempo: 68,
        popularity: 49,
        acousticness: 0.41,
        why: '7분 동안 당신을 서서히 무너뜨립니다. 실험적이고 필사적입니다.',
      },
      {
        id: 'e5',
        title: 'When The Morning Comes',
        artist: 'Odesza',
        album: 'In Return',
        imgId: 'photo-1540039155733-5bb30b53aa14',
        duration: '4:58',
        energy: 0.67,
        valence: 0.73,
        danceability: 0.62,
        tempo: 118,
        popularity: 55,
        acousticness: 0.12,
        why: '빛이 서서히 방을 채우는 것처럼. 새벽 5시의 희망.',
      },
    ],
  },
  {
    id: 'sage',
    name: 'Sage',
    tagline: '포커스 & 플로우 마스터',
    bio: 'Sage는 집중력과 생산성을 위한 음악만 선별합니다. 가사가 없거나 최소화된, 일정한 BPM, 중간 에너지의 음악.',
    color: '#a9f5c3',
    gradientClass: 'gradient-sage',
    emoji: '🌿',
    traits: [
      { label: 'Energy', value: 0.52 },
      { label: 'Valence', value: 0.55 },
      { label: 'Danceability', value: 0.48 },
      { label: 'Acousticness', value: 0.38 },
    ],
    preferredGenres: ['Electronic', 'Neo-Classical', 'Jazz', 'Instrumental'],
    curatingNow: '"Deep Work Session IV"',
    followers: 18564,
    playlist: [
      {
        id: 's1',
        title: 'Intro',
        artist: 'The xx',
        album: 'xx',
        imgId: 'photo-1516450360452-9312f5e86fc7',
        duration: '2:07',
        energy: 0.24,
        valence: 0.42,
        danceability: 0.52,
        tempo: 90,
        popularity: 74,
        acousticness: 0.78,
        why: '2분간 완벽한 집중 상태로 진입하는 통로.',
      },
      {
        id: 's2',
        title: 'Moon River (Instrumental)',
        artist: 'Henry Mancini',
        album: 'Breakfast at Tiffany\'s',
        imgId: 'photo-1471478331149-c72f17e33c73',
        duration: '2:41',
        energy: 0.18,
        valence: 0.68,
        danceability: 0.28,
        tempo: 68,
        popularity: 61,
        acousticness: 0.92,
        why: '시간이 부드럽게 흘러갑니다. 클래식의 힘.',
      },
      {
        id: 's3',
        title: 'Experience',
        artist: 'Ludovico Einaudi',
        album: 'In a Time Lapse',
        imgId: 'photo-1614613535308-eb5fbd3d2c17',
        duration: '5:14',
        energy: 0.31,
        valence: 0.51,
        danceability: 0.34,
        tempo: 76,
        popularity: 77,
        acousticness: 0.96,
        why: '피아노 하나로 세계를 만드는 방법. 몰입의 정석.',
      },
      {
        id: 's4',
        title: 'Flume',
        artist: 'Bon Iver',
        album: 'For Emma, Forever Ago',
        imgId: 'photo-1493225457124-a3eb161ffa5f',
        duration: '3:39',
        energy: 0.21,
        valence: 0.38,
        danceability: 0.36,
        tempo: 82,
        popularity: 65,
        acousticness: 0.87,
        why: '숲 속 오두막에 있는 기분. 창의적 사고가 자연스럽게 열립니다.',
      },
      {
        id: 's5',
        title: 'Comptine d\'un autre été',
        artist: 'Yann Tiersen',
        album: 'Amélie OST',
        imgId: 'photo-1470225620780-dba8ba36b745',
        duration: '2:22',
        energy: 0.14,
        valence: 0.62,
        danceability: 0.31,
        tempo: 75,
        popularity: 72,
        acousticness: 0.97,
        why: '단순한 멜로디가 반복될수록 더 깊이 빠져듭니다.',
      },
    ],
  },
]

export const featuredCollabs = [
  {
    id: 'c1',
    title: 'Luna × Echo: 새벽 3시의 발견',
    description: '잠 못 드는 밤, 두 AI가 함께 만든 몽환적 인디 컬렉션',
    personas: ['luna', 'echo'],
    trackCount: 18,
    imgId: 'photo-1516450360452-9312f5e86fc7',
  },
  {
    id: 'c2',
    title: 'Nova × Sage: 집중하며 즐기는 법',
    description: '에너지를 유지하면서도 흐름을 잃지 않는 균형점',
    personas: ['nova', 'sage'],
    trackCount: 24,
    imgId: 'photo-1598387993211-5a498de24cef',
  },
]
