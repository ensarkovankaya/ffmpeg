from django.test import TestCase

from ffmpeg.generator import Command
from ffmpeg.codecs import Codec
from ffmpeg.filters import BitstreamChannelFilter, FFmpegFilter, ScaleFilter, FOAR
from ffmpeg.utils import StreamSpecifier


class FFmpegTestCase(TestCase):
    def test_codec(self):
        c = Codec(copy=True, stream=StreamSpecifier.Video)
        c.validate()

    def test_bitstreamchannelfilter(self):
        bsf = BitstreamChannelFilter(stream=StreamSpecifier.Audio, filters=[FFmpegFilter.aac_adtstoasc])
        bsf.validate()

    def test_scalefilter_with_command(self):
        input = "input.mp4"
        output = "output.mp4"
        cmd = Command(input=input, output=output)
        self.assertEqual(cmd.generate(), '/usr/bin/ffmpeg -i "input.mp4" "output.mp4"')
        cmd.add_filter(ScaleFilter(width=1920, height=1080))
        self.assertEqual(cmd.generate(), '/usr/bin/ffmpeg -i "input.mp4" -filter:v scale=1920:1080 "output.mp4"')

    def test_scalefilter(self):
        f1 = ScaleFilter(width=1920, height=1080)
        self.assertEqual(f1.generate(), "-filter:v scale=1920:1080")

        f2 = ScaleFilter(uiw=True, uih=True)
        self.assertEqual(f2.generate(), "-filter:v scale=iw:ih")

        f3 = ScaleFilter(width=1920, uih=True)
        self.assertEqual(f3.generate(), "-filter:v scale=1920:ih")

        f4 = ScaleFilter(height=1080, uiw=True)
        self.assertEqual(f4.generate(), "-filter:v scale=iw:1080")

        f5 = ScaleFilter(uih=True, uiw=True, scale_width=2, scale_height=2)
        self.assertEqual(f5.generate(), "-filter:v scale=iw*2:ih*2")

        f6 = ScaleFilter(uiw=True, uih=True, kar=True, scale_width=3)
        self.assertEqual(f6.generate(), "-filter:v scale=iw*3:-1")

        f7 = ScaleFilter(uih=True, uiw=True, foar=FOAR.Decrease, scale_width=3)
        self.assertEqual(f7.generate(), "-filter:v scale=iw*3:ih:force_original_aspect_ratio=decrease")

    def test_command(self):
        input = "input.mp4"
        output = "output.mp4"
        duration = "00:10:00"

        cmd = Command(input=input, output=output, duration=duration)
        self.assertEqual(cmd.generate(), '/usr/bin/ffmpeg -i "input.mp4" -t 00:10:00 "output.mp4"')

        cmd.add_codec(Codec(copy=True, stream=StreamSpecifier.Video))
        self.assertEqual(cmd.generate(), '/usr/bin/ffmpeg -i "input.mp4" -t 00:10:00 -c:v copy "output.mp4"')

        cmd.add_filter(BitstreamChannelFilter(stream=StreamSpecifier.Audio, filters=[FFmpegFilter.aac_adtstoasc]))
        self.assertEqual(cmd.generate(),
                         '/usr/bin/ffmpeg -i "input.mp4" -t 00:10:00 -c:v copy -bsf:a aac_adtstoasc "output.mp4"')
