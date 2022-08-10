import dataclasses

__all__ = ("EphyrInstance",)

from typing import Optional


@dataclasses.dataclass
class EphyrInstance:
    ipv4: str
    """ IPv4 address of the instance. """
    domain: Optional[str] = None
    """ Useful for making links. """
    title: Optional[str] = None
    """ Human-readable name of that instance. """
    password: Optional[str] = None
    """ Leave None to access without password. """
    https: Optional[bool] = True
    """ Impacts port: 443 for https=True, 80 for https=False """

    @property
    def ip(self) -> str:
        return self.ipv4

    @property
    def host(self) -> str:
        return self.domain or self.ipv4
        # return self.ipv4

    @property
    def port(self) -> int:
        return 433 if self.https else 80

    @property
    def scheme(self) -> str:
        return "https" if self.https else "http"

    def print(self):
        address = (
            f"{self.scheme}://{self.domain if self.domain else self.ipv4}/"
        )
        print(
            f'Ephyr instance "{self.title}" at {address}'
            f'{" (" + str(self.ipv4) + ")" if self.domain else ""}'
        )
        print(f"Ephyr suggested password: {self.password}")
