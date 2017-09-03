from django.conf import settings
from django.utils.translation import ugettext as _

DEFAULT_LOG_LEVELS = [
    ("quiet", _("Quite")),
    ("panic", _("Panic")),
    ("fatal", _("Fatal")),
    ("error", _("Error")),
    ("warning", _("Warning")),
    ("info", _("Info")),
    ("verbose", _("Verbose")),
    ("debug", _("Debug")),
    ("trace", _("Trace")),
]

LOG_LEVELS = getattr(settings, "FFMPEG_LOG_LEVELS", DEFAULT_LOG_LEVELS)
