import json
import os
import platform
import subprocess
from logging import getLogger

from django.conf import settings

logger = getLogger('ffmpeg.utils.ffprobe')


def get_ffprobe_path():
    """Ask the system to ffprobe path"""
    # TODO: Make this Windows compatible

    if platform.system() in ['Linux', 'Darwin']:
        DEFAULT_FFPROBE_PATH = "/usr/bin/ffprobe"
        try:
            ps = subprocess.run(["which", "ffprobe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=1, check=True)
            path = ps.stdout.decode("utf-8").strip()
            return path or DEFAULT_FFPROBE_PATH
        except Exception as err:
            logger.warning("Could not ask Ffprobe path to the system.\n%s" % err)
    return None


FFPROBE_PATH = getattr(settings, "FFPROBE_PATH", None)
if FFPROBE_PATH is None:
    FFPROBE_PATH = get_ffprobe_path()

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
