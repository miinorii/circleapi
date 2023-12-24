from __future__ import annotations
from enum import IntEnum
from typing import Literal
from datetime import datetime
import msgspec


# https://osu.ppy.sh/docs/index.html#scopes
ApiScope = Literal["chat.write", "delegate", "forum.write", "friends.read", "identify", "public"]

# https://osu.ppy.sh/docs/index.html#ruleset
Ruleset = Literal["fruits", "mania", "osu", "taiko"]
RankStatusString = Literal["graveyard", "wip", "pending", "ranked", "approved", "qualified", "loved"]
Mod = Literal["HD", "DT", "HR", "FL", "NF", "NC", "SD", "SO", "PF", "EZ", "HT", "TD"]
Rank = Literal["F", "D", "C", "B", "A", "S", "X", "SH", "XH"]
ScoreScope = Literal["global", "country"]
RankStatus = Literal["graveyard", "wip", "pending", "ranked", "approved", "qualified", "loved"]
PlayStyle = Literal["mouse", "keyboard", "tablet", "touch"]
ProfilePage = Literal["me", "recent_activity", "beatmaps", "historical", "kudosu", "top_ranks", "medals"]


def sanitize_name(name: str) -> str:
    # If a renamed name exist return it, else return the original name
    return {
        "cover_2x": "cover@2x",
        "card_2x": "card@2x",
        "list_2x": "list@2x",
        "slimcover_2x": "slimcover@2x"
    }.get(name, name)


class RankStatusInt(IntEnum):
    # https://osu.ppy.sh/docs/index.html#beatmapsetcompact-rank-status
    graveyard = -2
    wip = -1
    pending = 0
    ranked = 1
    approved = 2
    qualified = 3
    loved = 4


class RulesetInt(IntEnum):
    OSU = 0
    TAIKO = 1
    FRUITS = 2
    MANIA = 3


class BaseStruct(msgspec.Struct):
    def __hash__(self):
        return hash(self.__repr__())

    def to_dict(self) -> dict:
        def _recursive_to_dict(data: msgspec.Struct) -> dict:
            new_dict = msgspec.structs.asdict(data)
            for key in new_dict:
                if isinstance(new_dict[key], msgspec.Struct):
                    new_dict[key] = _recursive_to_dict(new_dict[key])
                elif isinstance(new_dict[key], list):
                    for index, value in enumerate(new_dict[key]):
                        if isinstance(value, msgspec.Struct):
                            new_dict[key][index] = _recursive_to_dict(value)
            return new_dict
        return _recursive_to_dict(self)


class Covers(BaseStruct, kw_only=True, rename=sanitize_name):
    cover: str
    cover_2x: str
    card: str
    card_2x: str
    list: str
    list_2x: str
    slimcover: str
    slimcover_2x: str


class Availability(BaseStruct, kw_only=True):
    download_disabled: bool
    more_information: str | None = None


class Nominations(BaseStruct, kw_only=True):
    current: int
    required: int


class Hype(BaseStruct, kw_only=True):
    current: int
    required: int


class Failtimes(BaseStruct, kw_only=True):
    exit: list[int] | None = None
    fail: list[int] | None = None


class Beatmap(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmap
    # Required
    beatmapset_id: int
    difficulty_rating: float
    id: int
    mode: Ruleset
    status: RankStatus
    total_length: int
    user_id: int
    version: str

    # Optional
    beatmapset: Beatmapset | None = None
    max_combo: int | None = None
    checksum: str | None = None
    failtimes: Failtimes | None = None


class BeatmapExtended(Beatmap, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmapextended
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
    mode_int: RulesetInt
    passcount: int
    playcount: int
    ranked: RankStatusInt
    url: str

    # Optional
    beatmapset: BeatmapsetExtended | None = None
    deleted_at: datetime | None = None
    bpm: float | None = None


class Beatmaps(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#get-beatmaps
    beatmaps: list[BeatmapExtended]


class Beatmapset(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmapset
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
    spotlight: bool
    title: str
    title_unicode: str
    user_id: int
    video: bool

    # Optional
    offset: int | None
    beatmaps: list[BeatmapExtended] | None = None
    #converts: None  # TODO
    #current_user_attributes: None  # TODO
    #description: None  # TODO
    #discussions: None  # TODO
    #events: None  # TODO
    #genre: None  # TODO
    has_favourited: bool | None = None
    #language: None  # TODO
    nominations_summary: Nominations | None = None
    pack_tags: list[str] | None = None
    ratings: list[int] | None = None
    #recent_favourites: None  # TODO
    #related_users: None  # TODO
    #user: None  # TODO
    track_id: int | None = None


class BeatmapsetExtended(Beatmapset, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmapsetextended
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
    deleted_at: datetime | None = None

    # Derpecated
    discussion_enabled: bool | None = None


class StatisticsOsu(BaseStruct, kw_only=True):
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int


class Country(BaseStruct, kw_only=True):
    code: str
    name: str


class Cover(BaseStruct, kw_only=True):
    url: str
    custom_url: str | None = None
    id: int | None = None


class UserAccountHistory(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#usercompact-useraccounthistory
    id: int
    length: int
    permanent: bool
    timestamp: datetime
    type: Literal["note", "restriction", "silence"]
    description: str | None = None


class ProfileBanner(BaseStruct, kw_only=True):
    id: int
    tournament_id: int
    image: str


class UserBadge(BaseStruct, kw_only=True):
    awarded_at: datetime
    description: str
    image_url: str
    url: str


class UserGroup(BaseStruct, kw_only=True):
    has_listing: bool
    has_playmodes: bool
    id: int
    identifier: str
    is_probationary: bool
    name: str
    short_name: str
    colour: str | None = None
    playmodes: list[Ruleset] | None = None


class UserMonthlyPlaycount(BaseStruct, kw_only=True):
    count: int
    start_date: str


class UserPage(BaseStruct, kw_only=True):
    html: str
    raw: str


class RankHighest(BaseStruct, kw_only=True):
    rank: int
    updated_at: datetime


class RankHistory(BaseStruct, kw_only=True):
    mode: Ruleset
    data: list[int]


class UserLevel(BaseStruct, kw_only=True):
    current: int
    progress: int


class UserGradeCounts(BaseStruct, kw_only=True):
    a: int
    s: int
    sh: int
    ss: int
    ssh: int


class UserStatistics(BaseStruct, kw_only=True):
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


class UserStatisticsRulesets(BaseStruct, kw_only=True):
    osu: UserStatistics
    taiko: UserStatistics
    fruits: UserStatistics
    mania: UserStatistics


class UserAchievement(BaseStruct, kw_only=True):
    achieved_at: datetime
    achievement_id: int


class UserReplayWatchcount(BaseStruct, kw_only=True):
    start_date: str
    count: int


class User(BaseStruct, kw_only=True):
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


class UserKudosu(BaseStruct, kw_only=True):
    available: int
    total: int


class UserExtended(User, kw_only=True):
    has_supported: bool
    join_date: datetime
    kudosu: UserKudosu
    max_blocks: int
    max_friends: int
    playmode: Ruleset
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


class Score(BaseStruct, kw_only=True):
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
    mode: Ruleset
    mode_int: RulesetInt
    replay: bool

    # Optional
    beatmap_id: int | None = None
    pp: float | None = None
    user: User | None = None
    beatmap: BeatmapExtended | None = None
    rank_global: int | None = None


class BeatmapUserScore(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmapuserscore
    position: int
    score: Score


class BeatmapUserScores(BaseStruct, kw_only=True):
    scores: list[Score]


class BeatmapScores(BaseStruct, kw_only=True):
    # https://osu.ppy.sh/docs/index.html#beatmapset
    scores: list[Score]
    scope: ScoreScope
    beatmap_id: int
    user_score: BeatmapUserScore | None = None


class BeatmapDifficultyAttributes(BaseStruct, kw_only=True):
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
    great_hit_window: float | None = None

    # fruits

    # mania
    score_multiplier: float | None = None


class BeatmapAttributes(BaseStruct, kw_only=True):
    attributes: BeatmapDifficultyAttributes
    beatmap_id: int


class TokenPayload(BaseStruct, kw_only=True):
    aud: int
    jti: str
    iat: float
    nbf: float
    exp: float
    scopes: list[ApiScope]
    sub: int | None = None
