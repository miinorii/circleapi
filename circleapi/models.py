from __future__ import annotations
from pydantic import BaseModel, Field
from enum import IntEnum
from typing import Literal
from datetime import datetime


# https://osu.ppy.sh/docs/index.html#scopes
ApiScope = Literal["chat.write", "delegate", "forum.write", "friends.read", "identify", "public"]

# https://osu.ppy.sh/docs/index.html#gamemode
GameMode = Literal["fruits", "mania", "osu", "taiko"]
RankStatusString = Literal["graveyard", "wip", "pending", "ranked", "approved", "qualified", "loved"]
Mod = Literal["HD", "DT", "HR", "FL", "NF", "NC", "SD", "SO", "PF", "EZ", "HT", "TD"]
Rank = Literal["F", "D", "C", "B", "A", "S", "X", "SH", "XH"]
ScoreScope = Literal["global", "country"]
RankStatus = Literal["graveyard", "wip", "pending", "ranked", "approved", "qualified", "loved"]
PlayStyle = Literal["mouse", "keyboard", "tablet", "touch"]
ProfilePage = Literal["me", "recent_activity", "beatmaps", "historical", "kudosu", "top_ranks", "medals"]


class RankStatusInt(IntEnum):
    # https://osu.ppy.sh/docs/index.html#beatmapsetcompact-rank-status
    graveyard = -2
    wip = -1
    pending = 0
    ranked = 1
    approved = 2
    qualified = 3
    loved = 4


class GameModeInt(IntEnum):
    OSU = 0
    TAIKO = 1
    FRUITS = 2
    MANIA = 3


class Covers(BaseModel):
    cover: str
    cover_2x: str = Field(alias="cover@2x")
    card: str
    card_2x: str = Field(alias="card@2x")
    list: str
    list_2x: str = Field(alias="list@2x")
    slimcover: str
    slimcover_2x: str = Field(alias="slimcover@2x")


class Availability(BaseModel):
    download_disabled: bool
    more_information: str | None = None


class Nominations(BaseModel):
    current: int
    required: int


class Hype(BaseModel):
    current: int
    required: int


class Failtimes(BaseModel):
    exit: list[int] | None = None
    fail: list[int] | None = None


class BeatmapCompact(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapcompact
    # Required
    beatmapset_id: int
    difficulty_rating: float
    id: int
    mode: GameMode
    status: RankStatus
    total_length: int
    user_id: int
    version: str

    # Optional
    beatmapset: BeatmapsetCompact | None = None
    max_combo: int | None = None
    checksum: str | None = None
    failtimes: Failtimes | None = None


class Beatmap(BeatmapCompact):
    # https://osu.ppy.sh/docs/index.html#beatmap
    # Required
    accuracy: float
    ar: float
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    drain: float
    hit_length: int
    is_scoreable: bool
    last_updated: datetime
    mode_int: GameModeInt
    passcount: int
    playcount: int
    ranked: RankStatusInt
    url: str

    # Optional
    beatmapset: Beatmapset | None = None
    deleted_at: datetime | None = None
    bpm: float | None = None


class Beatmaps(BaseModel):
    # https://osu.ppy.sh/docs/index.html#get-beatmaps
    beatmaps: list[Beatmap]


class BeatmapsetCompact(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapsetcompact
    # Required
    artist: str
    artist_unicode: str
    covers: Covers
    creator: str
    favourite_count: int
    id: int
    nsfw: bool
    play_count: int
    preview_url: str
    source: str
    status: RankStatusString
    title: str
    title_unicode: str
    user_id: int
    video: bool

    # Optional
    offset: int | None
    beatmaps: list[Beatmap] | None = None
    #converts: None  # TODO
    #current_user_attributes: None  # TODO
    #description: None  # TODO
    #discussions: None  # TODO
    #events: None  # TODO
    #genre: None  # TODO
    has_favourited: bool | None = None
    #language: None  # TODO
    nominations: Nominations | None = None
    pack_tags: list[str] | None = None
    ratings: list[int] | None = None
    #recent_favourites: None  # TODO
    #related_users: None  # TODO
    #user: None  # TODO


class Beatmapset(BeatmapsetCompact):
    # https://osu.ppy.sh/docs/index.html#beatmapset
    # Required
    availability: Availability
    bpm: float
    can_be_hyped: bool
    discussion_locked: bool
    is_scoreable: bool
    last_updated: datetime
    nominations: Nominations | None = None
    ranked: RankStatusInt
    storyboard: bool
    tags: str

    # Optional
    hype: Hype | None = None
    legacy_thread_url: str | None = None
    submitted_date: datetime | None = None
    ranked_date: datetime | None = None


class StatisticsOsu(BaseModel):
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int


class Country(BaseModel):
    code: str
    name: str


class Cover(BaseModel):
    custom_url: str | None = None
    url: str
    id: int | None = None


class UserAccountHistory(BaseModel):
    # https://osu.ppy.sh/docs/index.html#usercompact-useraccounthistory
    id: int
    length: int
    permanent: bool
    timestamp: datetime
    type: Literal["note", "restriction", "silence"]
    description: str | None = None


class ProfileBanner(BaseModel):
    id: int
    tournament_id: int
    image: str


class UserBadge(BaseModel):
    awarded_at: datetime
    description: str
    image_url: str
    url: str

class UserGroup(BaseModel):
    has_listing: bool
    has_playmodes: bool
    id: int
    identifier: str
    is_probationary: bool
    name: str
    short_name: str
    colour: str | None = None
    playmodes: list[GameMode] | None = None


class UserMonthlyPlaycount(BaseModel):
    count: int
    start_date: str


class UserPage(BaseModel):
    html: str
    raw: str


class RankHighest(BaseModel):
    rank: int
    updated_at: datetime


class RankHistory(BaseModel):
    mode: GameMode
    data: list[int]


class UserLevel(BaseModel):
    current: int
    progress: int


class UserGradeCounts(BaseModel):
    a: int
    s: int
    sh: int
    ss: int
    ssh: int


class UserStatistics(BaseModel):
    count_300: int
    count_100: int
    count_50: int
    count_miss: int
    level: UserLevel
    pp: float
    ranked_score: int
    hit_accuracy: float
    play_count: int
    play_time: int
    total_score: int
    total_hits: int
    maximum_combo: int
    replays_watched_by_others: int
    is_ranked: bool
    grade_counts: UserGradeCounts
    global_rank: int | None = None
    country_rank: int | None = None


class UserStatisticsRulesets(BaseModel):
    osu: UserStatistics
    taiko: UserStatistics
    fruits: UserStatistics
    mania: UserStatistics


class UserAchievement(BaseModel):
    achieved_at: datetime
    achievement_id: int


class UserReplayWatchcount(BaseModel):
    start_date: str
    count: int


class UserCompact(BaseModel):
    # https://osu.ppy.sh/docs/index.html#usercompact
    # Required
    avatar_url: str
    country_code: str
    id: int
    is_active: bool
    is_bot: bool
    is_deleted: bool
    is_online: bool
    is_supporter: bool
    pm_friends_only: bool
    username: str

    # Optional
    default_group: str | None = None
    last_visit: datetime | None = None
    profile_colour: str | None = None
    country: Country | None = None
    cover: Cover | None = None
    account_history: list[UserAccountHistory] | None = None
    active_tournament_banner: ProfileBanner | None = None
    badges: list[UserBadge] | None = None
    beatmap_playcounts_count: int | None = None
    favourite_beatmapset_count: int | None = None
    follower_count: int | None = None
    graveyard_beatmapset_count: int | None = None
    groups: list[UserGroup] | None = None
    guest_beatmapset_count: int | None = None
    is_restricted: bool | None = None
    loved_beatmapset_count: int | None = None
    mapping_follower_count: int | None = None
    monthly_playcounts: list[UserMonthlyPlaycount] | None = None
    page: UserPage | None = None
    pending_beatmapset_count: int | None = None
    previous_usernames: list[str] | None = None
    rank_highest: RankHighest | None = None
    rank_history: RankHistory | None = None
    ranked_beatmapset_count: int | None = None
    replays_watched_counts: list[UserReplayWatchcount] | None = None
    scores_best_count: int | None = None
    scores_first_count: int | None = None
    scores_recent_count: int | None = None
    statistics: UserStatistics | None = None
    statistics_rulesets: UserStatisticsRulesets | None = None
    support_level: int | None = None
    unread_pm_count: int | None = None
    user_achievements: list[UserAchievement] | None = None


class UserKudosu(BaseModel):
    available: int
    total: int


class User(UserCompact):
    has_supported: bool
    join_date: datetime
    kudosu: UserKudosu
    max_blocks: int
    max_friends: int
    playmode: GameMode
    playstyle: list[PlayStyle]
    post_count: int
    profile_order: list[ProfilePage]
    discord: str | None = None
    interests: str | None = None
    location: str | None = None
    occupation: str | None = None
    title: str | None = None
    title_url: str | None = None
    twitter: str | None = None
    website: str | None = None



class Score(BaseModel):
    # https://osu.ppy.sh/docs/index.html#score
    # Required
    id: int
    best_id: int
    user_id: int
    accuracy: float
    mods: list[Mod]
    score: int
    max_combo: int
    perfect: bool
    statistics: StatisticsOsu
    passed: bool
    rank: Rank
    created_at: datetime
    mode: GameMode
    mode_int: GameModeInt
    replay: bool

    # Optional
    pp: float | None = None
    user: UserCompact | None = None
    beatmap: Beatmap | None = None
    rank_global: int | None = None


class BeatmapUserScore(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapuserscore
    position: int
    score: Score


class BeatmapUserScores(BaseModel):
    scores: list[Score]


class GetBeatmapScoresArgs(BaseModel):
    beatmap_id: int
    mode: GameMode | None = None
    mods: list[Mod] | None = None
    scope: ScoreScope = "global"


class BeatmapScores(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapset
    scores: list[Score]
    user_score: BeatmapUserScore | None = None
    args: GetBeatmapScoresArgs | None = None


class BeatmapDifficultyAttributes(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapdifficultyattributes
    # Required
    max_combo: int
    star_rating: float

    # Optional
    # osu
    aim_difficulty: float | None = None
    approach_rate: float | None = None
    flashlight_difficulty: float | None = None
    overall_difficulty: float | None = None
    slider_factor: float | None = None
    speed_difficulty: float | None = None

    # taiko
    stamina_difficulty: float | None = None
    rhythm_difficulty: float | None = None
    colour_difficulty: float | None = None
    approach_rate: float | None = None
    great_hit_window: float | None = None

    # fruits
    approach_rate: float | None = None

    # mania
    great_hit_window: float | None = None
    score_multiplier: float | None = None


class BeatmapAttributes(BaseModel):
    attributes: BeatmapDifficultyAttributes


class TokenPayload(BaseModel):
    aud: int
    jti: str
    iat: float
    nbf: float
    exp: float
    sub: int | None = None
    scopes: list[ApiScope]


# pydantic forward refs
Beatmap.model_rebuild()

