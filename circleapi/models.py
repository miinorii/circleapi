from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
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

class RankStatusInt(Enum):
    # https://osu.ppy.sh/docs/index.html#beatmapsetcompact-rank-status
    graveyard = -2
    wip = -1
    pending = 0
    ranked = 1
    approved = 2
    qualified = 3
    loved = 4


class GameModeInt(Enum):
    OSU = 0
    TAIKO = 1
    FRUITS = 2
    MANIA = 3


class Covers(BaseModel):
    cover: str
    cover_2x: str
    card: str
    card_2x: str
    list: str
    list_2x: str
    slimcover: str
    slimcover_2x: str

    class Config:
        fields = {"cover_2x": "cover@2x",
                  "card_2x": "card@2x",
                  "list_2x": "list@2x",
                  "slimcover_2x": "slimcover@2x"}


class Availability(BaseModel):
    download_disabled: bool
    more_information: str | None


class Nominations(BaseModel):
    current: int
    required: int


class Hype(BaseModel):
    current: int
    required: int


class Failtimes(BaseModel):
    exit: list[int] | None
    fail: list[int] | None


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
    beatmapset: Beatmapset | BeatmapsetCompact | None
    max_combo: int | None
    checksum: str | None
    failtimes: Failtimes | None


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
    deleted_at: datetime | None
    bpm: float | None


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
    beatmaps: list[Beatmap] | None
    #converts: None  # TODO
    #current_user_attributes: None  # TODO
    #description: None  # TODO
    #discussions: None  # TODO
    #events: None  # TODO
    #genre: None  # TODO
    has_favourited: bool | None
    #language: None  # TODO
    nominations: Nominations | None
    pack_tags: list[str] | None
    ratings: list[int] | None
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
    nominations: Nominations
    ranked: RankStatusInt
    storyboard: bool
    tags: str

    # Optional
    hype: Hype | None
    legacy_thread_url: str | None
    submitted_date: datetime | None
    ranked_date: datetime | None


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
    custom_url: str | None
    url: str
    id: int | None


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
    default_group: str | None
    last_visit: datetime | None
    profile_colour: str | None
    country: Country | None
    cover: Cover | None


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
    pp: float | None
    user: UserCompact | None
    beatmap: Beatmap | None
    rank_global: int | None


class BeatmapUserScore(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapuserscore
    position: int
    score: Score


class BeatmapUserScores(BaseModel):
    scores: list[Score]


class BeatmapScores(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapset
    scores: list[Score]
    user_score: BeatmapUserScore | None


class BeatmapDifficultyAttributes(BaseModel):
    # https://osu.ppy.sh/docs/index.html#beatmapdifficultyattributes
    # Required
    max_combo: int
    star_rating: float

    # Optional
    # osu
    aim_difficulty: float | None
    approach_rate: float | None
    flashlight_difficulty: float | None
    overall_difficulty: float | None
    slider_factor: float | None
    speed_difficulty: float | None

    # taiko
    stamina_difficulty: float | None
    rhythm_difficulty: float | None
    colour_difficulty: float | None
    approach_rate: float | None
    great_hit_window: float | None

    # fruits
    approach_rate: float | None

    # mania
    great_hit_window: float | None
    score_multiplier: float | None


class BeatmapAttributes(BaseModel):
    attributes: BeatmapDifficultyAttributes


class TokenPayload(BaseModel):
    aud: int
    jti: str
    iat: float
    nbf: float
    exp: float
    sub: int | None
    scopes: list[ApiScope]


# pydantic forward refs
Beatmap.update_forward_refs()

