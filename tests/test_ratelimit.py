import unittest
import time
from circleapi import RateLimit


class TestRateLimit(unittest.TestCase):
    def test_req_per_min_over_60(self):
        # around 16.6 req/s
        rate_limit = RateLimit(1000)

        for _ in range(16):
            self.assertFalse(rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(rate_limit.is_exceeded(), "Test if exceeded")

        # refill bucket
        time.sleep(1)

        for _ in range(16):
            self.assertFalse(rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(rate_limit.is_exceeded(), "Test if exceeded")

    def test_req_per_min_under_60(self):
        # around 0.333 req/s
        rate_limit = RateLimit(20)
        self.assertFalse(rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(rate_limit.is_exceeded(), "Test if exceeded")

        time.sleep(1)
        self.assertTrue(rate_limit.is_exceeded(), "Test if exceeded")
        time.sleep(1)
        self.assertTrue(rate_limit.is_exceeded(), "Test if exceeded")
        time.sleep(1)
        self.assertFalse(rate_limit.is_exceeded(), "Test if not exceeded")


if __name__ == "__main__":
    unittest.main()
