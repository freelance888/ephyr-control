import dataclasses

__all__ = ('EphyrInstance',)


@dataclasses.dataclass
class EphyrInstance:
    ipv4: str
    domain: str = None
    title: str = None
    password: str = None
    https: bool = True

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
        return 'https' if self.https else 'http'

    def print(self):
        address = f'{self.scheme}://{self.domain if self.domain else self.ipv4}/'
        print(f'Ephyr instance "{self.title}" at {address}{" (" + str(self.ipv4) + ")" if self.domain else ""}')
        print(f'Ephyr suggested password: {self.password}')

