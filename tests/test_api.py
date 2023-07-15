import unittest
import os
import warnings
from circleapi import (
    UserToken, ApiV2, Beatmap,
    BeatmapUserScore, BeatmapUserScores, BeatmapScores,
    Beatmaps, BeatmapAttributes, setup_queue_logging,
    Score, ExternalApi, Beatmapset
)
from dotenv import dotenv_values


TEST_DIR = os.path.realpath(os.path.dirname(__file__))


class TestApiV2Live(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = setup_queue_logging(to_console=True)
        cls.log.start()
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        env = dotenv_values(os.path.join(TEST_DIR, ".env"))
        token = UserToken(
            int(env["CLIENT"]),
            env["SECRET"],
            filepath=os.path.join(TEST_DIR, "user_token")
        )
        token.check_token()
        cls.api = ApiV2(token)
        cls.api.start_client()

    @classmethod
    def tearDownClass(cls):
        cls.api.stop_client()
        cls.log.stop()

    def test_beatmap_lookup(self):
        data = self.api.beatmap_lookup(beatmap_id=53)
        self.assertIsInstance(data, Beatmap)
        self.assertIsInstance(data.beatmapset, Beatmapset)

    def test_get_user_beatmap_score(self):
        data = self.api.get_user_beatmap_score(22423, 2, "osu")
        self.assertIsInstance(data, BeatmapUserScore)

    def test_get_user_beatmap_scores(self):
        data = self.api.get_user_beatmap_scores(22423, 2, "osu")
        self.assertIsInstance(data, BeatmapUserScores)

    def test_get_beatmap_scores(self):
        data = self.api.get_beatmap_scores(53, mode="osu", scope="global")
        self.assertIsInstance(data, BeatmapScores)

    def test_get_beatmaps(self):
        data = self.api.get_beatmaps([53, 55])
        self.assertIsInstance(data, Beatmaps)
        self.assertEqual(2, len(data.beatmaps))

    def test_get_beatmap(self):
        data = self.api.get_beatmap(53)
        self.assertIsInstance(data, Beatmap)

    def test_get_beatmap_attributes(self):
        data = self.api.get_beatmap_attributes(53)
        self.assertIsInstance(data, BeatmapAttributes)

    def test_get_score(self):
        data = self.api.get_score("osu", 1720541511)
        self.assertIsInstance(data, Score)


class TestExternalApiLive(unittest.TestCase):
    def test_get_ranked_ids(self):
        ranked = ExternalApi.get_ranked_ids()
        self.assertIn(53, ranked)

    def test_get_loved_ids(self):
        loved = ExternalApi.get_loved_ids()
        self.assertIn(24722, loved)

    def test_get_ranked_and_loved_ids(self):
        ranked_and_loved = ExternalApi.get_ranked_and_loved_ids()
        self.assertIn(53, ranked_and_loved)
        self.assertIn(24722, ranked_and_loved)


if __name__ == "__main__":
    unittest.main()
