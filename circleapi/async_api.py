from .logger import logger
from .models import (
    BeatmapScores, GameMode, ScoreScope,
    Beatmap, Mod, BeatmapUserScore,
    BeatmapUserScores, Beatmaps, BeatmapAttributes,
    Score
)
from .async_token import AsyncUserToken, AsyncGuestToken
import time
import httpx
import random
import asyncio


class AsyncRateLimit:
    def __init__(self, req_per_minute):
        self._lock = asyncio.Lock()
        self.set_rate_limit(req_per_minute)

    def set_rate_limit(self, req_per_minute: int):
        self.max_req_per_sec = req_per_minute / 60
        self.bucket_limit = 1 if self.max_req_per_sec < 1 else self.max_req_per_sec
        self.bucket = self.bucket_limit
        self.last_req_ts = int(time.time())

    async def is_exceeded(self):
        """
        Token bucket algorithm

        Return True if empty
        """
        async with self._lock:
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


class AsyncApiV2:
    def __init__(self, token: AsyncGuestToken | AsyncUserToken):
        self.timeout = httpx.Timeout(20, read=240)
        self.token = token
        self.rate_limit = AsyncRateLimit(1000)
        self._global_client = False
        self._lock = asyncio.Lock()

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout,
            base_url="https://osu.ppy.sh/api/v2"
        )

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._global_client:
            return self._create_client()
        with self._lock:
            if self._client.is_closed:
                await self.start_client()
                logger.warning("ApiV2 pool renewed")
        return self._client

    async def start_client(self):
        self._global_client = True
        self._client = await self._create_client().__aenter__()

    async def stop_client(self, exc_type=None, exc_val=None, exc_tb=None):
        self._global_client = False
        if not self._client.is_closed:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        await self.start_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_client(exc_type, exc_val, exc_tb)

    async def _request(
            self,
            method: str,
            url: str,
            params: dict | str | None = None,
            json_data: dict | None = None,
            args: dict | None = None,
            validate_with=None):

        # Rate limit check
        while await self.rate_limit.is_exceeded():
            await asyncio.sleep(random.randint(1, 4))

        # Token validity check
        await self.token.check_token()

        client = await self._get_client()
        try:
            req = await client.request(
                method=method,
                url=url,
                headers=self.token.headers,
                params=params,
                json=json_data
            )
        finally:
            if not self._global_client and not client.is_closed:
                await client.aclose()

        req.raise_for_status()
        logger.info(f"[  \033[32mOK\033[0m  ] {url} {params=} {json_data=}")
        data = validate_with(**req.json())
        return data

    async def beatmap_lookup(self,
                       checksum: str | None = None,
                       filename: str | None = None,
                       beatmap_id: int | None = None) -> Beatmap:
        # https://osu.ppy.sh/docs/index.html#lookup-beatmap
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if checksum: params["checksum"] = checksum
        if filename: params["filename"] = filename
        if beatmap_id: params["id"] = beatmap_id

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/lookup",
            "params": params,
            "validate_with": Beatmap,
            "args": params
        }

        return await self._request(**kwargs)

    async def get_user_beatmap_score(self,
                               beatmap_id: int,
                               user_id: int,
                               mode: GameMode | None = None,
                               mods: list[Mod] | None = None) -> BeatmapUserScore:
        # https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-score
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode
        if mods: params["mods"] = mods

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores/users/{user_id}",
            "params": params,
            "validate_with": BeatmapUserScore,
            "args": {"beatmap": beatmap_id, "user": user_id, **params}
        }

        return await self._request(**kwargs)

    async def get_user_beatmap_scores(self,
                               beatmap_id: int,
                               user_id: int,
                               mode: GameMode | None = None) -> BeatmapUserScores:
        # https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-scores
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores/users/{user_id}/all",
            "params": params,
            "validate_with": BeatmapUserScores,
            "args": {"beatmap": beatmap_id, "user": user_id, **params}
        }

        return await self._request(**kwargs)

    async def get_beatmap_scores(self,
                           beatmap_id: int,
                           mode: GameMode | None = None,
                           mods: list[Mod] | None = None,
                           scope: ScoreScope | None = None) -> BeatmapScores:
        # https://osu.ppy.sh/docs/index.html#get-beatmap-scores
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode
        if mods: params["mods"] = mods
        if scope: params["type"] = scope

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores",
            "params": params,
            "validate_with": BeatmapScores,
            "args": {"beatmap": beatmap_id, **params}
        }

        return await self._request(**kwargs)

    async def get_beatmaps(self,
                     ids: list[int]) -> Beatmaps:
        # https://osu.ppy.sh/docs/index.html#get-beatmaps
        await self.token.has_scope("public", raise_exception=True)

        params = "&".join([f"ids[]={beatmap_id}" for beatmap_id in ids])
        kwargs = {
            "method": "GET",
            "url": f"/beatmaps",
            "params": params,
            "validate_with": Beatmaps,
            "args": {"ids": ids}
        }

        return await self._request(**kwargs)

    async def get_beatmap(self,
                     beatmap_id: int) -> Beatmap:
        # https://osu.ppy.sh/docs/index.html#get-beatmap
        await self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}",
            "params": {},
            "validate_with": Beatmap,
            "args": {"beatmap": beatmap_id}
        }

        return await self._request(**kwargs)

    async def get_beatmap_attributes(self,
                               beatmap_id: int,
                               mods: list[Mod] | None = None,
                               ruleset: GameMode | None = None,
                               ruleset_id: int | None = None) -> BeatmapAttributes:
        # https://osu.ppy.sh/docs/index.html#get-beatmap-attributes
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if mods: params["mods"] = mods
        if ruleset: params["ruleset"] = ruleset
        if ruleset_id: params["ruleset_id"] = ruleset_id

        kwargs = {
            "method": "POST",
            "url": f"/beatmaps/{beatmap_id}/attributes",
            "json_data": params,
            "validate_with": BeatmapAttributes,
            "args": {"beatmap": beatmap_id, **params}
        }

        return await self._request(**kwargs)

    async def get_score(self,
                  mode: GameMode,
                  score_id: int) -> Score:
        # https://osu.ppy.sh/docs/index.html#get-apiv2scoresmodescore
        await self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/scores/{mode}/{score_id}",
            "validate_with": Score,
            "args": {"mode": mode, "score": score_id}
        }

        return await self._request(**kwargs)


class AsyncExternalApi:
    @staticmethod
    async def get_ranked_ids() -> list[int]:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://osu.lea.moe/beatmaps")
        l = r.json()["ranked"]["beatmaps"]
        l.sort()
        return l

    @staticmethod
    async def get_loved_ids() -> list[int]:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://osu.lea.moe/beatmaps")
        l = r.json()["loved"]["beatmaps"]
        l.sort()
        return l

    @staticmethod
    async def get_ranked_and_loved_ids() -> list[int]:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://osu.lea.moe/beatmaps")
        data = r.json()
        l = list(set(data["ranked"]["beatmaps"]) | set(data["loved"]["beatmaps"]))
        l.sort()
        return l