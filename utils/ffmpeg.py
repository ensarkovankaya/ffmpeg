import os
import platform
import re
import subprocess
from logging import getLogger

from django.conf import settings

logger = getLogger("ffmpeg.utils")


def get_ffmpeg_path():
    """Ask the system to ffmpeg path"""
    # TODO: Make this Windows compatible

    if platform.system() in ['Linux', 'Darwin']:
        DEFAULT_FFMPEG_PATH = "/usr/bin/ffmpeg"
        try:
            ps = subprocess.run(["which", "ffmpeg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1,
                                check=True)
            path = ps.stdout.decode("utf-8").strip()
            return path or DEFAULT_FFMPEG_PATH
        except Exception as err:
            logger.warning("Could not ask FFmpeg path to the system.\n%s" % err)

    return None


FFMPEG_PATH = getattr(settings, "FFMPEG_PATH", None)
if FFMPEG_PATH is None:
    FFMPEG_PATH = get_ffmpeg_path()

if not os.path.exists(FFMPEG_PATH):
    raise ValueError("FFmpeg not found in system, path: %s" % FFMPEG_PATH)


def get_formats():
    """Get available File Formats

    Basically runs `ffmpeg -formats` and parse the results
    :return [{
        'format': str,
        'Demuxing Supported': bool,
        'Muxing Supported': bool,
        'display': str
    }]
    """

    try:
        # Ask ffmpeg to formats
        ps = subprocess.run([FFMPEG_PATH, "-formats", "-v", "error"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=1, check=True)
        output = ps.stdout.decode("utf-8")
        pattern = "\s(D|\s)(E|\s)\s([a-zA-Z0-9_,]+)\s+(.+)\n"
        findings = re.findall(pattern, output)
        formats = []
        # Parse the results
        for f in findings:
            for format in f[3].split(','):
                formats.append({
                    'format': format,
                    'Demuxing Supported': f[0] == 'D',
                    'Muxing Supported': f[1] == 'E',
                    'display': f[4]
                })
        return formats
    except Exception:
        logger.exception("Could not get formats.")
        raise


def get_codecs(only_video=False, only_audio=False, only_subtitle=False):
    """Gets available codecs
    Basically runs `ffmpeg -codecs` and parse the results
    :return [{
        'codec': str,
        'Decoding supported': bool,
        'Encoding supported': bool,
        'Video codec': bool,
        'Audio codec': bool,
        'Subtitle codec': bool,
        'Intra frame-only codec': bool,
        'Lossy compression': bool,
        'Lossless compression': bool,
        'display': str
    }]
    """

    VIDEO_CODECS = []
    AUDIO_CODECS = []
    SUBTITLE_CODECS = []
    CODECS = []

    try:
        ps = subprocess.run([FFMPEG_PATH, "-codecs", "-v", "error"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=1, check=True)
        output = ps.stdout.decode("utf-8")
        pattern = "\s(D|\.)(E|\.)(V|A|S|\.)(I|\.)(L|\.)(S|\.)\s([a-zA-Z0-9_,]+)\s+(.+)\n"
        findings = re.findall(pattern, output)

        for f in findings:
            for codec in f[6].split(','):
                c = {
                    'name': codec,
                    'Decoding supported': f[0] == 'D',
                    'Encoding supported': f[1] == 'E',
                    'Video codec': f[2] == 'V',
                    'Audio codec': f[2] == 'A',
                    'Subtitle codec': f[2] == 'S',
                    'Intra frame-only codec': f[3] == 'I',
                    'Lossy compression': f[4] == 'L',
                    'Lossless compression': f[5] == 'S',
                    'display': f[6]
                }
                if only_video and f[2] == 'V':
                    VIDEO_CODECS.append(c)
                elif only_audio and f[2] == 'A':
                    AUDIO_CODECS.append(c)
                elif only_subtitle and f[2] == 'S':
                    SUBTITLE_CODECS.append(c)
                else:
                    CODECS.append(c)
    except Exception:
        logger.exception("Could not get codecs.")
        raise

    if only_video:
        return VIDEO_CODECS
    if only_audio:
        return AUDIO_CODECS
    if only_subtitle:
        return SUBTITLE_CODECS
    return CODECS


def get_bitstream_filters():
    try:
        ps = subprocess.run([FFMPEG_PATH, "-bsfs", "-v", "error"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=1, check=True)
        output = ps.stdout.decode("utf-8")
        pattern = "[a-zA-Z0-9_]\n"
        return re.findall(pattern, output)
    except Exception:
        logger.exception("Could not get bitstream filters.")
        raise
