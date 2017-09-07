from django.test import TestCase

from ffmpeg.generator import Command
from ffmpeg.utils.codecs import Codec
from ffmpeg.utils.filters import StreamSpecifier, BitstreamChannelFilter, FFmpegFilter


class FFmpegTestCase(TestCase):
    def test_codec(self):
        c = Codec({"copy": True, "stream": StreamSpecifier.Video.value})
        c.validate()

    def test_bitstreamchannelfilter(self):
        bsf = BitstreamChannelFilter(
            {"stream": StreamSpecifier.Audio.value, "filters": FFmpegFilter.aac_adtstoasc.value}
        )
        bsf.validate()

    def test_command(self):
        input = "http://trtcanlitv-lh.akamaihd.net/i/TRTAVAZ_1@182244/index_1000_av-b.m3u8?sd=10&rebase=on"
        output = "output.mp4"
        duration = "00:10:00"

        cmd = Command(data={'input': input, 'output': output, 'duration': duration})
        cmd.add_codec(Codec(data={"copy": True, "stream": StreamSpecifier.Video.value}))

        cmd.add_filter(BitstreamChannelFilter(
                {"stream": StreamSpecifier.Audio.value, "filters": FFmpegFilter.aac_adtstoasc.value}
            )
        )

        print(cmd.generate(as_str=True))
