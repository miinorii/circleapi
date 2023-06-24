from .logger import logger
from .models import TokenPayload, ApiScope
from .utils import InvalidApiScope, extract_payload_from_token
import httpx
import time
import socket
import threading


class GuestToken:
    def __init__(
            self,
            client_id: int | None = None,
            client_secret: str | None = None,
            payload: TokenPayload | None = None,
            filepath: str | None = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.payload = payload
        self.access_token = None
        self._file = None
        self._lock = threading.Lock()

        if filepath:
            try:
                self.load_from_file(filepath, enable_auto_update=True)
            except FileNotFoundError:
                logger.warning("Loading token from file failed: file does not exist")

    def has_scope(self, scope: ApiScope, raise_exception: bool = False) -> bool:
        if not self.payload:
            self.check_token()
        in_payload = scope in self.payload.scopes
        if raise_exception and not in_payload:
            raise InvalidApiScope(scope)
        return in_payload

    def load_from_file(self, filepath: str, enable_auto_update: bool = False):
        """
        Load an access token (first line)
        """
        if enable_auto_update:
            self._file = filepath
        with open(filepath, "r") as f:
            lines = f.readlines()
            if len(lines) != 1:
                raise ValueError("Invalid file format")
            access_token = lines[0].strip()
        self.access_token = access_token
        self.payload = extract_payload_from_token(self.access_token)

    def export_to_file(self, filename: str, enable_auto_update: bool = False):
        if enable_auto_update:
            self._file = filename
        with open(filename, "w") as f:
            f.write(f"{self.access_token}")

    def check_token(self, force_refresh=False):
        """
        Check if the current access token is valid, renew it otherwise.
        Return False if the token is invalid

        :return:
        """
        with self._lock:
            if not self.access_token \
                    or not self.payload \
                    or time.time() > self.payload.exp - 3600 \
                    or force_refresh:
                logger.info(f"Refreshing guest token ... | {force_refresh=} {time.time()}:{self.payload.exp - 3600 if self.payload else 0}")
                self._request_token()
                if self._file:
                    self.export_to_file(self._file)
                logger.info("Guest token refreshed")
                return False
            return True

    def _request_token(self):
        """
        Request an access token from osu! api with the provided client_id and client_secret

        :return:
        """
        post_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'public'
        }
        req = httpx.post('https://osu.ppy.sh/oauth/token', data=post_data)
        req.raise_for_status()
        res = req.json()
        self.access_token = res["access_token"]
        self.payload = extract_payload_from_token(self.access_token)

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }


class UserToken:
    def __init__(self,
                 client_id: int | None = None,
                 client_secret: str | None = None,
                 payload: TokenPayload | None = None,
                 filepath: str | None = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.payload = payload
        self.access_token = None
        self.refresh_token = None
        self._file = None
        self._lock = threading.Lock()

        if filepath:
            try:
                self.load_from_file(filepath, enable_auto_update=True)
            except FileNotFoundError:
                logger.warning("Loading token from file failed: file does not exist")

    def has_scope(self, scope: ApiScope, raise_exception: bool = False) -> bool:
        if not self.payload:
            self.check_token()
        in_payload = scope in self.payload.scopes
        if raise_exception and not in_payload:
            raise InvalidApiScope(scope)
        return in_payload

    def load_from_file(self, filepath: str, enable_auto_update: bool = False):
        """
        Load an access token (first line) with its refresh token (second line)
        """
        if enable_auto_update:
            self._file = filepath
        with open(filepath, "r") as f:
            lines = f.readlines()
            if len(lines) != 2:
                raise ValueError("Invalid file format")
            access_token = lines[0].strip()
            refresh_token = lines[1].strip()
        self._update_token_info(access_token, refresh_token)

    def export_to_file(self, filename: str, enable_auto_update: bool = False):
        with open(filename, "w") as f:
            f.write(f"{self.access_token}\n{self.refresh_token}")
        if enable_auto_update:
            self._file = filename

    def check_token(self, force_renew=False, force_refresh=False) -> bool:
        """
        Check if the current access token is valid, refresh it otherwise.
        Return False if the token is invalid

        :return:
        """

        with self._lock:
            if not self.access_token or not self.refresh_token or not self.payload or force_renew:
                logger.info(f"Manually renewing user token ...")
                self._renew_token()
                if self._file:
                    self.export_to_file(self._file)
                logger.info(f"Manually renewed user token")
                return False

            if time.time() > self.payload.exp - 3600 or force_refresh:
                logger.info(f"Refreshing user token ... | {force_refresh=} {time.time()}:{self.payload.exp - 3600}")
                self._refresh_token()
                if self._file:
                    self.export_to_file(self._file)
                logger.info("User token refreshed")
                return False
            return True

    def _refresh_token(self):
        post_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }

        req = httpx.post('https://osu.ppy.sh/oauth/token', data=post_data)
        req.raise_for_status()
        res = req.json()
        self._update_token_info(res["access_token"], res["refresh_token"])

    def _renew_token(self):
        """
        Complete renewal of the token, require manual actions

        :return:
        """

        if not self.client_id:
            raise ValueError("Client id is missing")

        if not self.client_secret:
            raise ValueError("Secret id is missing")

        print(f"Open this link:\n"
              f"https://osu.ppy.sh/oauth/authorize?client_id={self.client_id}"
              f"&redirect_uri=http://127.0.0.1/api&response_type=code&scope=public")

        server_address = ("localhost", 80)
        print(f"Listening on {server_address[0]}:{server_address[1]} for a response code ...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(server_address)
            s.listen()
            conn, addr = s.accept()
            authorization_code = conn.recv(8192).decode().split()[1].split("/api?code=")[-1]
            conn.send(b"HTTP/1.1 200 OK\n"
                  b"Content-Type: text/html\n\n"
                  b"<html><body><h1>Authorization code received !</h1></body></html>\n")
        print(f"Authorization code received !")

        # Prepare post data
        post_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://127.0.0.1/api'
        }

        req = httpx.post('https://osu.ppy.sh/oauth/token', data=post_data)
        req.raise_for_status()
        res = req.json()
        self._update_token_info(res["access_token"], res["refresh_token"])

    def _update_token_info(self, access_token: str, refresh_token: str):
        """
        Update access_token, refresh_token and payload

        :param access_token:
        :param refresh_token:
        :return:
        """

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.payload = extract_payload_from_token(access_token)

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
