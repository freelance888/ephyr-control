import dataclasses
import logging
import time

import requests
import yarl

__all__ = ("Pinger",)


@dataclasses.dataclass
class Pinger:
    host: str
    port: int = None
    protocol: str = "http"
    username: str = None
    password: str = None

    path: str = None
    query: dict = None
    fragment: str = None

    user_agent: str = "Pinger (Python requests)"

    timeout: float = 10
    max_retries: int = 3

    do_raise: bool = True
    do_raise_for_status: bool = True
    do_report_error: bool = False
    loglevel: str = logging.INFO

    target_url: yarl.URL = dataclasses.field(init=False)
    logger: logging.Logger = dataclasses.field(init=False)

    def __post_init__(self):
        self.target_url = self.build_url()
        self.logger = logging.getLogger(f"Pinger {self.target}")

    def build_url(self) -> yarl.URL:
        return yarl.URL.build(
            scheme=self.protocol,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.path or "",
            query=self.query,
            fragment=self.fragment or "",
        )

    def build_headers(self) -> dict:
        headers = {}
        if self.user_agent is not None:
            headers["User-Agent"] = self.user_agent
        return headers

    def ping(self) -> bool:
        self.logger.debug(f"Pinging {self.target} ...")
        success = self._ping()
        if success:
            self.logger.info(f"Successful ping from {self.target}")
        else:
            self.logger.warning(f"Failed to ping {self.target}")
        return success

    def retrying_ping(self) -> bool:
        self.logger.info(f"Immediate first attempt to ping {self.target} :")
        try:
            success = self.ping()
        except IOError:
            ...
        else:
            if success:
                return True

        for attempt in range(2, self.max_retries + 1):
            self.logger.debug(f"Waiting for {self.timeout} second ...")
            self._wait(self.timeout)
            self.logger.info(f"{attempt}th attempt to ping {self.target} :")
            if self.ping():
                return True

        self.logger.warning(
            f"All {self.max_retries} attempts to ping {self.target} failed"
        )
        return False

    def interactive_ping(self) -> bool:
        gave_up = False
        while not gave_up:
            if self.retrying_ping():
                return True
            else:
                gave_up = input(
                    "Do you want continue ping attempts? (y/N) "
                ).lower() not in {"y", "yes"}

        return False

    @property
    def target(self) -> str:
        return str(self.target_url)

    @staticmethod
    def _requests_get(url: str, headers: dict) -> requests.Response:
        return requests.get(url, timeout=1, headers=headers)

    def _report_error(self, exc: Exception):
        self.logger.error(f"Failed to ping {self.target} due to error: {exc}")

    def _ping(self) -> bool:
        resp = None
        try:  # noqa: WPS229
            headers = self.build_headers()
            resp = self._requests_get(self.target, headers)
        except requests.exceptions.RequestException as exc:
            if self.do_report_error:
                self._report_error(exc=exc)
            if self.do_raise:
                raise
            return False
        finally:
            if resp:
                self.logger.debug(
                    f"Response: [{len(resp.content)}] {resp.content}"  # noqa: WPS237
                )

        if not self.do_raise_for_status:
            return resp.ok

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if self.do_report_error:
                self._report_error(exc=exc)
            if self.do_raise:
                raise
            return False
        else:
            return True

    @staticmethod
    def _wait(seconds: float):
        time.sleep(seconds)
