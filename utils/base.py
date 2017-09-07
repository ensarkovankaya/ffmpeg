from enum import Enum

from django import forms


class StreamSpecifier(Enum):
    Video = "v"
    Audio = "a"
    Subtitle = "s"


class BaseCommand(forms.Form):
    args = []

    def validate(self):
        if not self.is_valid():
            raise ValueError(
                "%s is not valid.\nData: %s\nErrors: %s" % (self.__class__.__name__, self.data, self.errors))
        return self

    def generate(self, as_str: bool = False):
        """This should generates a string as command run on shell"""
        raise NotImplemented()


class BaseFilter(BaseCommand):
    stream = forms.ChoiceField(choices=[(s.value, s.name) for s in StreamSpecifier],
                               initial=StreamSpecifier.Video.value, required=True)
