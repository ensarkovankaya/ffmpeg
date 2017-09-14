import inspect
from enum import Enum

from django import forms
from django.utils.translation import ugettext_lazy as _


class ChoiceEnum(Enum):
    __translatable__ = True

    @classmethod
    def choices(cls):
        return [(v.value, _(v.name) if cls.__translatable__ else v.name) for v in cls]

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.__dict__.values())

    @classmethod
    def values(cls):
        return [v.value for v in cls]


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
    def validate(self):
        if not self.is_valid():
            raise ValueError(
                "%s is not valid.\nData: %s\nErrors: %s" % (self.__class__.__name__, self.data, self.errors))
        return self

    def generate(self, as_str: bool = True):
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
