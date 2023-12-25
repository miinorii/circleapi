from .logger import logger
from .models import (
    BeatmapScores, Ruleset, ScoreScope,
    BeatmapExtended, Mod, BeatmapUserScore,
    BeatmapUserScores, BeatmapsExtended, BeatmapAttributes,
    Score, UserExtended
)
from .utils import AsyncRateLimit
from .async_token import AsyncUserToken, AsyncGuestToken
import httpx
import random
import asyncio
import msgspec


class AsyncApiV2:
    def __init__(self, token: AsyncGuestToken | AsyncUserToken):
        self.timeout = httpx.Timeout(20, read=240)
        self.token = token
        self.rate_limit = AsyncRateLimit(1000)
        self._global_client = False
        self._lock = asyncio.Lock()
        self._decoder = msgspec.json.Decoder()
        self._encoder = msgspec.json.Encoder()

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
            as_dict: bool = False,
            validate_with=None):

        # Rate limit check
        # Exponential backoff with a bit of randomness
        rate_limit_hit = 0
        while await self.rate_limit.is_exceeded():
            sleep_time = min(2 ** rate_limit_hit, 32) + random.randint(0, 1000) / 1000
            await asyncio.sleep(sleep_time)
            rate_limit_hit += 1

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

        # Dirty workaround to add some important values that are missing from api responses
        data: dict = self._decoder.decode(req.content)
        if args:
            data.update(args)
            if validate_with is BeatmapScores:
                for score in data["scores"]:
                    score.update(args)
                if data["user_score"]:
                    data["user_score"]["score"].update(args)
            elif validate_with is BeatmapUserScore:
                data["score"].update(args)
            elif validate_with is BeatmapUserScores:
                for score in data["scores"]:
                    score.update(args)

        if as_dict:
            return data
        else:
            return msgspec.json.decode(self._encoder.encode(data), type=validate_with, strict=False)

    async def beatmap_lookup(self,
                             checksum: str | None = None,
                             filename: str | None = None,
                             beatmap_id: int | None = None,
                             as_dict: bool = False) -> BeatmapExtended:
        # https://osu.ppy.sh/docs/index.html#lookup-beatmap
        await self.token.has_scope("public", raise_exception=True)

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
            "args": params,
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_user_beatmap_score(self,
                                     beatmap_id: int,
                                     user_id: int,
                                     mode: Ruleset | None = None,
                                     mods: list[Mod] | None = None,
                                     as_dict: bool = False) -> BeatmapUserScore:
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
            "args": {"args": {"beatmap_id": beatmap_id, "user_id": user_id, **params}, "beatmap_id": beatmap_id},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_user_beatmap_scores(self,
                                      beatmap_id: int,
                                      user_id: int,
                                      mode: Ruleset | None = None,
                                      as_dict: bool = False) -> BeatmapUserScores:
        # https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-scores
        await self.token.has_scope("public", raise_exception=True)

        params = {}
        if mode: params["mode"] = mode

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}/scores/users/{user_id}/all",
            "params": params,
            "validate_with": BeatmapUserScores,
            "args": {"args": {"beatmap_id": beatmap_id, "user_id": user_id, **params}, "beatmap_id": beatmap_id},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_beatmap_scores(self,
                                 beatmap_id: int,
                                 mode: Ruleset | None = None,
                                 mods: list[Mod] | None = None,
                                 scope: ScoreScope | None = None,
                                 as_dict: bool = False) -> BeatmapScores:
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
            "args": {"args": {"beatmap_id": beatmap_id, **params}, "beatmap_id": beatmap_id, "scope": scope},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_beatmaps(self, ids: list[int], as_dict: bool = False) -> BeatmapsExtended:
        # https://osu.ppy.sh/docs/index.html#get-beatmaps
        await self.token.has_scope("public", raise_exception=True)

        params = "&".join([f"ids[]={beatmap_id}" for beatmap_id in ids])
        kwargs = {
            "method": "GET",
            "url": f"/beatmaps",
            "params": params,
            "validate_with": BeatmapsExtended,
            "args": {"args": {"ids": ids}},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_beatmap(self, beatmap_id: int, as_dict: bool = False) -> BeatmapExtended:
        # https://osu.ppy.sh/docs/index.html#get-beatmap
        await self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/beatmaps/{beatmap_id}",
            "params": {},
            "validate_with": BeatmapExtended,
            "args": {"args": {"beatmap_id": beatmap_id}},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_beatmap_attributes(self,
                                     beatmap_id: int,
                                     mods: list[Mod] | None = None,
                                     ruleset: Ruleset | None = None,
                                     ruleset_id: int | None = None,
                                     as_dict: bool = False) -> BeatmapAttributes:
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
            "args": {"args": {"beatmap_id": beatmap_id, **params}, "beatmap_id": beatmap_id},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_score(self,
                        mode: Ruleset,
                        score_id: int,
                        as_dict: bool = False) -> Score:
        # https://osu.ppy.sh/docs/index.html#get-apiv2scoresmodescore
        await self.token.has_scope("public", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/scores/{mode}/{score_id}",
            "validate_with": Score,
            "args": {"args": {"mode": mode, "score_id": score_id}, "id": score_id},
            "as_dict": as_dict
        }

        return await self._request(**kwargs)

    async def get_own_data(self, mode: Ruleset | None = None, as_dict: bool = False) -> UserExtended:
        # https://osu.ppy.sh/docs/index.html#get-own-data
        await self.token.has_scope("identify", raise_exception=True)

        kwargs = {
            "method": "GET",
            "url": f"/me/{mode if mode else ''}",
            "validate_with": UserExtended,
            "args": {"args": {"mode": mode}},
            "as_dict": as_dict
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