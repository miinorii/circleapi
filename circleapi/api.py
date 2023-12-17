from .logger import logger
from .models import (
    BeatmapScores, Ruleset, ScoreScope,
    BeatmapExtended, Mod, BeatmapUserScore,
    BeatmapUserScores, Beatmaps, BeatmapAttributes,
    Score, UserExtended
)
from .token import GuestToken, UserToken
from copy import deepcopy
import msgspec
import time
import threading
import httpx
import random


class RequestThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None
        self.args = None

    def run(self):
        """
        Taken from python threading.Thread implementation:

            Method representing the thread's activity.

            You may override this method in a subclass. The standard run() method
            invokes the callable object passed to the object's constructor as the
            target argument, if any, with sequential and keyword arguments taken
            from the args and kwargs arguments, respectively.

        """
        try:
            if self._target is not None:
                self.args = deepcopy(self._kwargs.get("args") if self._kwargs.get("args") else {})
                self.result = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


class RateLimit:
    max_req_per_sec: float
    bucket_limit: float
    bucket: float
    last_req_ts: int

    def __init__(self, req_per_minute):
        self._lock = threading.Lock()
        self.set_rate_limit(req_per_minute)

    def set_rate_limit(self, req_per_minute: int):
        self.max_req_per_sec = req_per_minute / 60
        self.bucket_limit = 1 if self.max_req_per_sec < 1 else self.max_req_per_sec
        self.bucket = self.bucket_limit
        self.last_req_ts = int(time.time())

    def is_exceeded(self):
        """
        Token bucket algorithm

        Return True if empty
        """
        with self._lock:
            current_ts = int(time.time())
            time_passed = current_ts - self.last_req_ts
            self.last_req_ts = current_ts
            self.bucket = self.bucket + time_passed * self.max_req_per_sec

            if self.bucket > self.bucket_limit:
                self.bucket = self.bucket_limit

            if self.bucket < 1:
                logger.warning("Rate limit exceeded")
                return True
            else:
                self.bucket = self.bucket - 1
                return False


class ApiV2:
    def __init__(self, token: GuestToken | UserToken):
        self.timeout = httpx.Timeout(20, read=240)
        self.token = token
        self.rate_limit = RateLimit(1000)
        self._global_client = False
        self._lock = threading.Lock()

    def _create_client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout,
            base_url="https://osu.ppy.sh/api/v2"
        )

    def _get_client(self) -> httpx.Client:
        if not self._global_client:
            return self._create_client()
        with self._lock:
            if self._client.is_closed:
                self.start_client()
                logger.warning("ApiV2 pool renewed")
        return self._client

    def start_client(self):
        self._global_client = True
        self._client = self._create_client().__enter__()

    def stop_client(self, exc_type=None, exc_val=None, exc_tb=None):
        self._global_client = False
        if not self._client.is_closed:
            self._client.__exit__(exc_type, exc_val, exc_tb)

    def __enter__(self):
        self.start_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_client(exc_type, exc_val, exc_tb)

    def _request(
            self,
            method: str,
            url: str,
            params: dict | str | None = None,
            json_data: dict | None = None,
            args: dict | None = None,
            validate_with=None):

        # Rate limit check
        while self.rate_limit.is_exceeded():
            time.sleep(random.randint(1, 4))

        # Token validity check
        self.token.check_token()

        client = self._get_client()
        try:
            req = client.request(
                method=method,
                url=url,
                headers=self.token.headers,
                params=params,
                json=json_data
            )
        finally:
            if not self._global_client and not client.is_closed:
                client.close()

        req.raise_for_status()
        logger.info(f"[  \033[32mOK\033[0m  ] {url} {params=} {json_data=}")
        data = msgspec.json.decode(req.content, type=validate_with, strict=False)

        if hasattr(validate_with, "args"):
            data.args = args
        return data

    def beatmap_lookup(self,
                       checksum: str | None = None,
                       filename: str | None = None,
                       beatmap_id: int | None = None,
                       as_thread: bool = False) -> BeatmapExtended | RequestThread:
        # https://osu.ppy.sh/docs/index.html#lookup-beatmap
        self.token.has_scope("public", raise_exception=True)

        params = {}
        if checksum:
            params["checksum"] = checksum
        if filename:
            params["filename"] = filename
        if beatmap_id:
            params["id"] = beatmap_id

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/lookup",
            "params": params,
            "validate_with": BeatmapExtended,
            "args": params
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_user_beatmap_score(self,
                               beatmap_id: int,
                               user_id: int,
                               mode: Ruleset | None = None,
                               mods: list[Mod] | None = None,
                               as_thread: bool = False) -> BeatmapUserScore | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-score
        self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode
        if mods: params["mods"] = mods

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores/users/{user_id}",
            "params": params,
            "validate_with": BeatmapUserScore,
            "args": {"beatmap_id": beatmap_id, "user_id": user_id, **params}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_user_beatmap_scores(self,
                                beatmap_id: int,
                                user_id: int,
                                mode: Ruleset | None = None,
                                as_thread: bool = False) -> BeatmapUserScores | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-scores
        self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores/users/{user_id}/all",
            "params": params,
            "validate_with": BeatmapUserScores,
            "args": {"beatmap_id": beatmap_id, "user_id": user_id, **params}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_beatmap_scores(self,
                           beatmap_id: int,
                           mode: Ruleset | None = None,
                           mods: list[Mod] | None = None,
                           scope: ScoreScope = "global",
                           as_thread: bool = False) -> BeatmapScores | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-beatmap-scores
        self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode
        if mods: params["mods"] = mods
        if scope: params["type"] = scope

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores",
            "params": params,
            "validate_with": BeatmapScores,
            "args": {"beatmap_id": beatmap_id, **params}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_beatmaps(self,
                     ids: list[int],
                     as_thread: bool = False) -> Beatmaps | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-beatmaps
        self.token.has_scope("public", raise_exception=True)

        params = "&".join([f"ids[]={beatmap_id}" for beatmap_id in ids])
        kwargs = {
            "method": "GET",
            "url": f"/beatmaps",
            "params": params,
            "validate_with": Beatmaps,
            "args": {"ids": ids}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_beatmap(self,
                     beatmap_id: int,
                     as_thread: bool = False) -> BeatmapExtended | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-beatmap
        self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}",
            "params": {},
            "validate_with": BeatmapExtended,
            "args": {"beatmap_id": beatmap_id}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_beatmap_attributes(self,
                               beatmap_id: int,
                               mods: list[Mod] | None = None,
                               ruleset: Ruleset | None = None,
                               ruleset_id: int | None = None,
                               as_thread: bool = False) -> BeatmapAttributes | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-beatmap-attributes
        self.token.has_scope("public", raise_exception=True)

        params = {}
        if mods: params["mods"] = mods
        if ruleset: params["ruleset"] = ruleset
        if ruleset_id: params["ruleset_id"] = ruleset_id

        kwargs = {
            "method": "POST",
            "url": f"/beatmaps/{beatmap_id}/attributes",
            "json_data": params,
            "validate_with": BeatmapAttributes,
            "args": {"beatmap_id": beatmap_id, **params}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_score(self,
                  mode: Ruleset,
                  score_id: int,
                  as_thread: bool = False) -> Score | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-apiv2scoresmodescore
        self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/scores/{mode}/{score_id}",
            "validate_with": Score,
            "args": {"mode": mode, "score_id": score_id}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

    def get_own_data(self,
                     mode: Ruleset | None = None,
                     as_thread: bool = False) -> UserExtended | RequestThread:
        # https://osu.ppy.sh/docs/index.html#get-own-data
        self.token.has_scope("identify", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/me/{mode if mode else ''}",
            "validate_with": UserExtended,
            "args": {"mode": mode}
        }

        if as_thread:
            return RequestThread(target=self._request, kwargs=kwargs)
        else:
            return self._request(**kwargs)

class ExternalApi:
    @staticmethod
    def get_ranked_ids() -> list[int]:
        r = httpx.get("https://osu.lea.moe/beatmaps")
        l = r.json()["ranked"]["beatmaps"]
        l.sort()
        return l

    @staticmethod
    def get_loved_ids() -> list[int]:
        r = httpx.get("https://osu.lea.moe/beatmaps")
        l = r.json()["loved"]["beatmaps"]
        l.sort()
        return l

    @staticmethod
    def get_ranked_and_loved_ids() -> list[int]:
        r = httpx.get("https://osu.lea.moe/beatmaps")
        data = r.json()
        l = list(set(data["ranked"]["beatmaps"]) | set(data["loved"]["beatmaps"]))
        l.sort()
        return l