from .models import TokenPayload
import base64
import json


class InvalidApiScope(Exception):
    def __init__(self, scope):
        self.message = "Scope not found in token payload: '{}'".format(scope)
        super().__init__(self.message)


def extract_payload_from_token(token) -> TokenPayload:
    raw_payload = token.split(".")[1]
    padding = "=" * (len(raw_payload) % 4)
    payload_bytes = base64.b64decode(raw_payload + padding)
    payload = json.loads(payload_bytes.decode("utf-8"))
    if not payload.get("sub"):
        payload["sub"] = None
    return TokenPayload(**payload)