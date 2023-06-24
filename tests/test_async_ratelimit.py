import unittest
from circleapi import AsyncRateLimit
import asyncio


class TestAsyncRateLimit(unittest.IsolatedAsyncioTestCase):
    async def test_req_per_min_over_60(self):
        # around 16.6 req/s
        rate_limit = AsyncRateLimit(1000)

        for _ in range(16):
            self.assertFalse(await rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(await rate_limit.is_exceeded(), "Test if exceeded")

        # refill bucket
        await asyncio.sleep(1)

        for _ in range(16):
            self.assertFalse(await rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(await rate_limit.is_exceeded(), "Test if exceeded")

    async def test_req_per_min_under_60(self):
        # around 0.333 req/s
        rate_limit = AsyncRateLimit(20)
        self.assertFalse(await rate_limit.is_exceeded(), "Test if not exceeded")
        self.assertTrue(await rate_limit.is_exceeded(), "Test if exceeded")

        await asyncio.sleep(1)
        self.assertTrue(await rate_limit.is_exceeded(), "Test if exceeded")
        await asyncio.sleep(1)
        self.assertTrue(await rate_limit.is_exceeded(), "Test if exceeded")
        await asyncio.sleep(1)
        self.assertFalse(await rate_limit.is_exceeded(), "Test if not exceeded")


if __name__ == "__main__":
    unittest.main()
