import inspect
from enum import Enum

from django import forms


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(v.value, v.name) for v in cls]

    def __str__(self):
        return self.value


class StreamSpecifier(ChoiceEnum):
    Video = "v"
    Audio = "a"
    Subtitle = "s"


class EnumChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        # Unpack Enum
        choices = kwargs.get('choices', None)
        if choices and inspect.isclass(choices) and issubclass(choices, ChoiceEnum):
            kwargs['choices'] = choices.choices()
        super(EnumChoiceField, self).__init__(*args, **kwargs)


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
    stream = EnumChoiceField(choices=StreamSpecifier, required=False)


def unrap_kwargs(**kwargs):
    # For Enums extract value for keys
    data: dict = kwargs.get('data', None)
    new_data = {}
    if data and isinstance(data, dict):
        for k, v in data.items():
            if inspect.isclass(v) and issubclass(v, Enum):
                new_data[k] = v.value
            else:
                new_data[k] = v
        kwargs['data'] = new_data
    return kwargs
