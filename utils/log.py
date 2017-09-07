from enum import Enum

from django.conf import settings
from django.utils.translation import ugettext as _


class LogLevel(Enum):
    Quite = "quite"
    Panic = "panic"
    Fatal = "fatal"
    Error = "error"
    Warning = "warning"
    Info = "info"
    Verbose = "verbose"
    Debug = "debug"
    Trace = "trace"


DEFAULT_LOG_LEVELS = [(l.value, _(l.name)) for l in LogLevel]

LOG_LEVELS = getattr(settings, "FFMPEG_LOG_LEVELS", DEFAULT_LOG_LEVELS)
