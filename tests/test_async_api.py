import unittest
import os
from circleapi import (
    AsyncApiV2, Beatmap, AsyncUserToken,
    BeatmapUserScore, BeatmapUserScores, BeatmapScores,
    Beatmaps, BeatmapAttributes, setup_queue_logging,
    Score, AsyncExternalApi, Beatmapset, User
)
from dotenv import dotenv_values


TEST_DIR = os.path.realpath(os.path.dirname(__file__))
env = dotenv_values(os.path.join(TEST_DIR, ".env"))
token = AsyncUserToken(
    int(env["CLIENT"]),
    env["SECRET"],
    filepath=os.path.join(TEST_DIR, "user_token")
)


class TestAsyncApiV2Live(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = setup_queue_logging(to_console=True)
        cls.log.start()
        cls.api = AsyncApiV2(token)

    @classmethod
    def tearDownClass(cls):
        cls.log.stop()

    async def test_get_own_data(self):
        data = await self.api.get_own_data()
        self.assertIsInstance(data, User)

    async def test_beatmap_lookup(self):
        data = await self.api.beatmap_lookup(beatmap_id=53)
        self.assertIsInstance(data, Beatmap)
        self.assertIsInstance(data.beatmapset, Beatmapset)

    async def test_get_user_beatmap_score(self):
        data = await self.api.get_user_beatmap_score(22423, 2, "osu")
        self.assertIsInstance(data, BeatmapUserScore)

    async def test_get_user_beatmap_scores(self):
        data = await self.api.get_user_beatmap_scores(22423, 2, "osu")
        self.assertIsInstance(data, BeatmapUserScores)

    async def test_get_beatmap_scores(self):
        data = await self.api.get_beatmap_scores(53, mode="osu", scope="global")
        self.assertIsInstance(data, BeatmapScores)
        self.assertEqual(53, data.args["beatmap_id"])
        self.assertEqual("global", data.args["type"])
        data = await self.api.get_beatmap_scores(53, mode="osu", scope="country")
        self.assertIsInstance(data, BeatmapScores)
        self.assertEqual(53, data.args["beatmap_id"])
        self.assertEqual("country", data.args["type"])

    async def test_get_beatmaps(self):
        data = await self.api.get_beatmaps([53, 55])
        self.assertIsInstance(data, Beatmaps)
        self.assertEqual(2, len(data.beatmaps))

    async def test_get_beatmap(self):
        data = await self.api.get_beatmap(53)
        self.assertIsInstance(data, Beatmap)

    async def test_get_beatmap_attributes(self):
        data = await self.api.get_beatmap_attributes(53)
        self.assertIsInstance(data, BeatmapAttributes)

    async def test_get_score(self):
        data = await self.api.get_score("osu", 1720541511)
        self.assertIsInstance(data, Score)


class TestExternalApiLive(unittest.IsolatedAsyncioTestCase):
    async def test_get_ranked_ids(self):
        ranked = await AsyncExternalApi.get_ranked_ids()
        self.assertIn(53, ranked)

    async def test_get_loved_ids(self):
        loved = await AsyncExternalApi.get_loved_ids()
        self.assertIn(24722, loved)

    async def test_get_ranked_and_loved_ids(self):
        ranked_and_loved = await AsyncExternalApi.get_ranked_and_loved_ids()
        self.assertIn(53, ranked_and_loved)
        self.assertIn(24722, ranked_and_loved)


if __name__ == "__main__":
    unittest.main()

