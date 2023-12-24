from .models import TokenPayload
from .logger import logger
from copy import deepcopy
import base64
import json
import threading
import time
import asyncio


class InvalidApiScope(Exception):
    def __init__(self, scope):
        self.message = "Scope not found in token payload: '{}'".format(scope)
        super().__init__(self.message)


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


class AsyncRateLimit:
    max_req_per_sec: float
    bucket_limit: float
    bucket: float
    last_req_ts: int

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


def extract_payload_from_token(token) -> TokenPayload:
    raw_payload = token.split(".")[1]
    padding = "=" * (len(raw_payload) % 4)
    payload_bytes = base64.b64decode(raw_payload + padding)
    payload = json.loads(payload_bytes.decode("utf-8"))
    if not payload.get("sub"):
        payload["sub"] = None
    return TokenPayload(**payload)