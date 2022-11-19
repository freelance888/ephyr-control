import dataclasses

__all__ = ("EphyrInstance",)

from typing import Optional

from ephyr_control.instance.protocols import EphyrInstanceProtocol
from ephyr_control.types import EphyrConfig


@dataclasses.dataclass(unsafe_hash=True)
class EphyrInstance(EphyrInstanceProtocol):
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
    https: bool = True

    @classmethod
    def from_config(cls, config: EphyrConfig):
        return cls(**config)

    @property
    def ip(self) -> str:
        return self.ipv4

    @property
    def host(self) -> str:
        return self.domain or self.ipv4

    @property
    def port(self) -> int:
        return 433 if self.https else 80

    @property
    def scheme(self) -> str:
        return "https" if self.https and self.domain else "http"

    def address(self, with_password=False):
        if with_password:
            return f"{self.scheme}://1:{self.password}@{self.host}/"
        return f"{self.scheme}://{self.host}/"

    def print(self):
        """Print data about itself."""
        extra = " (" + str(self.ipv4) + ")" if self.domain else ""
        print(f'Ephyr instance "{self.title}" at {self.address()}{extra}')
        print(f"Ephyr instance URL with password: {self.address(with_password=True)}")
        print(f"Ephyr suggested password: {self.password}")
