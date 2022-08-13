import dataclasses

__all__ = ("EphyrInstance",)

from typing import Optional


@dataclasses.dataclass
class EphyrInstance:
    """Ephyr instance - represents one server with its address.
    Connects to server using provided arguments and can perform simple actions on it.

    Arguments
    * ipv4: IPv4 address of the instance.
    * domain: Useful for making links.
    * title: Human-readable name of that instance.
    * password: Leave None to access without password.
    * https: Impacts port - 443 for https=True, 80 for https=False
    """

    ipv4: str
    domain: Optional[str] = None
    title: Optional[str] = None
    password: Optional[str] = None
    https: Optional[bool] = True

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
        host = self.domain if self.domain else self.ipv4
        address = f"{self.scheme}://{host}/"
        extra = " (" + str(self.ipv4) + ")" if self.domain else ""
        print(f'Ephyr instance "{self.title}" at {address}{extra}')
        print(f"Ephyr suggested password: {self.password}")
