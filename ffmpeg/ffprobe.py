import json
import os
import subprocess
from logging import getLogger

from django.conf import settings

logger = getLogger('ffmpeg.utils.ffprobe')

FFPROBE_PATH = getattr(settings, "FFPROBE_PATH", "/usr/bin/ffprobe")

if not os.path.exists(FFPROBE_PATH):
    raise FileNotFoundError("FFprobe can not found in system. %s" % FFPROBE_PATH)


def get_file_attributes(path):
    if not os.path.exists(path):
        raise FileNotFoundError("File not found in %s" % path)

    try:
        args = [FFPROBE_PATH, "-v", "error", "-show_format", "-show_streams", "-print_format", "json", "-i", path]
        ps = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return json.loads(ps.stdout.decode("utf-8"))
    except Exception as err:
        logger.exception("File attributes not get. Path: %s\n%s" % (path, err))
        raise err
