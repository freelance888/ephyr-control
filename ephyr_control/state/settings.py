import dataclasses

__all__ = ("Settings",)


@dataclasses.dataclass
class Settings:
    title: str = None
    delete_confirmation: bool = True
    enable_confirmation: bool = True

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "delete_confirmation": self.delete_confirmation,
            "enable_confirmation": self.enable_confirmation,
        }
