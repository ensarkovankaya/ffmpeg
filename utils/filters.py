from enum import Enum

from django import forms

from .base import BaseFilter, StreamSpecifier


class FFmpegFilter(Enum):
    text2movsub = "text2movsub"
    remove_extra = "remove_extra"
    noise = "noise"
    mov2textsub = "mov2textsub"
    mpeg4_unpack_bframes = "mpeg4_unpack_bframes"
    mp3decomp = "mp3decomp"
    mjpegadump = "mjpegadump"
    mjpeg2jpeg = "mjpeg2jpeg"
    imxdump = "imxdump"
    hevc_mp4toannexb = "hevc_mp4toannexb"
    h264_mp4toannexb = "h264_mp4toannexb"
    dump_extra = "dump_extra"
    chomp = "chomp"
    aac_adtstoasc = "aac_adtstoasc"


class BitstreamChannelFilter(BaseFilter):
    filters = forms.CharField(max_length=255)

    def generate(self, as_str: bool = False):
        self.args = ["-bsf:" + self.cleaned_data['stream'], self.cleaned_data['filters']]
        return " ".join(self.args) if as_str else self.args


class FOAR(Enum):
    Disable = "disable"
    Decrease = "decrease"
    Increase = "increase"


class ScaleFilter(BaseFilter):
    """# https://ffmpeg.org/ffmpeg-all.html#scale-1
    :return -filter:{stream} scale={width}x{height}

    # kar = True
    :return -filter:{stream} scale={width}x-1

    """
    stream = StreamSpecifier.Video.value

    width = forms.IntegerField(initial=0)
    height = forms.IntegerField(initial=0)

    use_input_width = forms.BooleanField(initial=False)  # Use input width as width
    use_input_height = forms.BooleanField(initial=False)  # Use input height as height

    scale_width = forms.IntegerField(max_value=10, min_value=1, required=False)
    scale_height = forms.IntegerField(max_value=10, min_value=1, required=False)

    kar = forms.BooleanField(initial=False)  # Keep Aspect Ratio
    foar = forms.ChoiceField(choices=[(c.value, c.name) for c in FOAR],
                             initial=FOAR.Disable.value)  # Force Original Aspect Ratio

    def clean(self):
        if self.cleaned_data['kar'] and self.cleaned_data['foar']:
            raise forms.ValidationError("KAR and FOAR can not be set True at the same time")
        return super(ScaleFilter, self).clean()

    def generate(self, as_str: bool = False):
        self.validate()
        width = "iw" if self.cleaned_data['use_input_width'] else self.cleaned_data['width']
        height = "ih" if self.cleaned_data['use_input_height'] else self.cleaned_data['height']

        width = width + "*" + self.cleaned_data['scale_width']
        height = height + "*" + self.cleaned_data['scale_height']

        scale = "scale=" + width + ":" + "-1" if self.cleaned_data['kar'] else height

        if self.cleaned_data['foar'] != FOAR.Disable.value:
            scale = scale + ":force_original_aspect_ratio=" + self.cleaned_data['foar']

        self.args = ["-filter:" + self.cleaned_data['stream'], scale]
        return " ".join(self.args) if as_str else self.args
