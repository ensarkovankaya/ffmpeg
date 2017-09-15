import inspect
from enum import Enum

from django import forms
from django.conf import settings
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


class LogLevel(ChoiceEnum):
    Quite = "quite"
    Panic = "panic"
    Fatal = "fatal"
    Error = "error"
    Warning = "warning"
    Info = "info"
    Verbose = "verbose"
    Debug = "debug"
    Trace = "trace"


DEFAULT_ASPECT_RATIOS = [
    (4 / 3, "4:3"),
    (16 / 9, "16:9")
]

ASPECT_RATIOS = getattr(settings, "FFMPEG_ASPECT_RATIOS", DEFAULT_ASPECT_RATIOS)

# https://ffmpeg.org/ffmpeg-utils.html#Video-size
DEFAULT_VIDEO_SIZES = [('720x480', 'NTSC 720x480'), ('720x576', 'PAL 720x576'),
                       ('352x240', 'QNTSC 352x240'), ('352x288', 'QPAL 352x288'), ('640x480', 'SNTSC 640x480'),
                       ('768x576', 'SPAL 768x576'), ('352x240', 'FILM 352x240'), ('352x240', 'NTSC-FILM 352x240'),
                       ('128x96', 'SQCIF 128x96'), ('176x144', 'QCIF 176x144'), ('352x288', 'CIF 352x288'),
                       ('704x576', '4CIF 704x576'), ('1408x1152', '16CIF 1408x1152'), ('160x120', 'QQVGA 160x120'),
                       ('320x240', 'QVGA 320x240'), ('640x480', 'VGA 640x480'), ('800x600', 'SVGA 800x600'),
                       ('1024x768', 'XGA 1024x768'), ('1600x1200', 'UXGA 1600x1200'), ('2048x1536', 'QXGA 2048x1536'),
                       ('1280x1024', 'SXGA 1280x1024'), ('2560x2048', 'QSXGA 2560x2048'),
                       ('5120x4096', 'HSXGA 5120x4096'), ('852x480', 'WVGA 852x480'), ('1366x768', 'WXGA 1366x768'),
                       ('1600x1024', 'WSXGA 1600x1024'), ('1920x1200', 'WUXGA 1920x1200'),
                       ('2560x1600', 'WOXGA 2560x1600'), ('3200x2048', 'WQSXGA 3200x2048'),
                       ('3840x2400', 'WQUXGA 3840x2400'), ('6400x4096', 'WHSXGA 6400x4096'),
                       ('7680x4800', 'WHUXGA 7680x4800'), ('320x200', 'CGA 320x200'), ('640x350', 'EGA 640x350'),
                       ('852x480', 'HD480 852x480'), ('1280x720', 'HD720 1280x720'), ('1920x1080', 'HD1080 1920x1080'),
                       ('2048x1080', '2K 2048x1080'), ('1998x1080', '2KFLAT 1998x1080'),
                       ('2048x858', '2KSCOPE 2048x858'), ('4096x2160', '4K 4096x2160'),
                       ('3996x2160', '4KFLAT 3996x2160'), ('4096x1716', '4KSCOPE 4096x1716'),
                       ('640x360', 'NHD 640x360'), ('240x160', 'HQVGA 240x160'), ('400x240', 'WQVGA 400x240'),
                       ('432x240', 'FWQVGA 432x240'), ('480x320', 'HVGA 480x320'), ('960x540', 'QHD 960x540'),
                       ('2048x1080', '2KDCI 2048x1080'), ('4096x2160', '4KDCI 4096x2160'),
                       ('3840x2160', 'UHD2160 3840x2160'), ('7680x4320', 'UHD4320 7680x4320')]

VIDEO_SIZES = getattr(settings, "FFMPEG_VIDEO_SIZES", DEFAULT_VIDEO_SIZES)

# https://ffmpeg.org/ffmpeg-utils.html#Video-rate
DEFAULT_VIDEO_RATES = [('ntsc', 'NTSC 30000/1001'), ('pal', 'PAL 25/1'),
                       ('qntsc', 'QNTSC 30000/1001'), ('qpal', 'QPAL 25/1'), ('sntsc', 'SNTSC 30000/1001'),
                       ('spal', 'SPAL 25/1'), ('film', 'FILM 24/1'), ('ntsc-film', 'NTSC-FILM 24000/1001')]

VIDEO_RATES = getattr(settings, "FFMPEG_VIDEO_RATES", DEFAULT_VIDEO_RATES)
