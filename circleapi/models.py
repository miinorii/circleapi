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


class BeatmapScores(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapset
    scores: list[Score]
    user_score: BeatmapUserScore | None = None


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

