from .mixin_output import Mixin, OutputWithMixins, UuidMixin, UuidOutputWithMixins
from .output import Output, UuidOutput
from .volume import Volume


def make_output(d: dict):
    if d["id"]:
        if d["mixins"]:
            return UuidOutputWithMixins.from_dict(d)
        return UuidOutput.from_dict(d)
    else:
        if d["mixins"]:
            return OutputWithMixins.from_dict(d)
        return Output.from_dict(d)
