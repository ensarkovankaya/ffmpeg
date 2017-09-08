from django.test import TestCase

from ffmpeg.generator import Command
from ffmpeg.utils.codecs import Codec
from ffmpeg.utils.filters import StreamSpecifier, BitstreamChannelFilter, FFmpegFilter, ScaleFilter, FOAR


class FFmpegTestCase(TestCase):
    def test_codec(self):
        c = Codec({"copy": True, "stream": StreamSpecifier.Video})
        c.validate()

    def test_bitstreamchannelfilter(self):
        bsf = BitstreamChannelFilter(
            {"stream": StreamSpecifier.Audio, "filters": FFmpegFilter.aac_adtstoasc}
        )
        bsf.validate()

    def test_scalefilter_with_command(self):
        input = "input.mp4"
        output = "output.mp4"
        cmd = Command(data={"input": input, "output": output})
        cmd.add_filter(ScaleFilter(data={"width": 1920, "height": 1080}))
        self.assertEqual(cmd.generate(as_str=True), "/usr/bin/ffmpeg -i input.mp4 -filter:v scale=1920:1080 output.mp4")

    def test_scalefilter(self):
        f1 = ScaleFilter(data={"width": 1920, "height": 1080})
        self.assertEqual(f1.generate(True), "-filter:v scale=1920:1080")

        f2 = ScaleFilter(data={"uiw": True, "uih": True})
        self.assertEqual(f2.generate(True), "-filter:v scale=iw:ih")

        f3 = ScaleFilter(data={"width": 1920, "uih": True})
        self.assertEqual(f3.generate(True), "-filter:v scale=1920:ih")

        f4 = ScaleFilter(data={"height": 1080, "uiw": True})
        self.assertEqual(f4.generate(True), "-filter:v scale=iw:1080")

        f5 = ScaleFilter(data={"uih": True, "uiw": True, "scale_width": 2, "scale_height": 2})
        self.assertEqual(f5.generate(True), "-filter:v scale=iw*2:ih*2")

        f6 = ScaleFilter(data={"uih": True, "uiw": True, "kar": True, "scale_width": 3})
        self.assertEqual(f6.generate(True), "-filter:v scale=iw*3:-1")

        f7 = ScaleFilter(data={"uih": True, "uiw": True, "foar": FOAR.Decrease, "scale_width": 3})
        self.assertEqual(f7.generate(True), "-filter:v scale=iw*3:ih:force_original_aspect_ratio=decrease")


def test_command(self):
    input = "input.mp4"
    output = "output.mp4"
    duration = "00:10:00"

    cmd = Command(data={'input': input, 'output': output, 'duration': duration})
    cmd.add_codec(Codec(data={"copy": True, "stream": StreamSpecifier.Video}))

    cmd.add_filter(BitstreamChannelFilter({"stream": StreamSpecifier.Audio, "filters": FFmpegFilter.aac_adtstoasc}))

    print(cmd.generate(as_str=True))
