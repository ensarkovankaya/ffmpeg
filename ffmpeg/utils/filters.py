from django import forms

from .base import BaseFilter, StreamSpecifier, EnumChoiceField, ChoiceEnum


class FFmpegFilter(ChoiceEnum):
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
    def __init__(self, stream: StreamSpecifier, filters: [FFmpegFilter]):
        data = {'stream': stream, 'filters': ",".join([f.value for f in filters])}
        super(BitstreamChannelFilter, self).__init__(data=data)

    filters = forms.CharField(max_length=255)

    def generate(self, as_str: bool = True):
        self.validate()
        args = ["-bsf:" + self.cleaned_data['stream'], self.cleaned_data['filters']]
        return " ".join(args) if as_str else args


class FOAR(ChoiceEnum):
    Disable = "disable"
    Decrease = "decrease"
    Increase = "increase"


class ScaleFilter(BaseFilter):
    """# https://ffmpeg.org/ffmpeg-all.html#scale-1
    :return -filter:{stream} scale={width}x{height}

    # kar = True
    :return -filter:{stream} scale={width}x-1

    """

    def __init__(self, uiw: bool = False, uih: bool = False, kar: bool = False, foar: FOAR = FOAR.Disable, **kwargs):
        kwargs['uiw'] = uiw
        kwargs['uih'] = uih
        kwargs['kar'] = kar
        kwargs['foar'] = foar
        kwargs['stream'] = StreamSpecifier.Video
        super(ScaleFilter, self).__init__(data=kwargs)

    width = forms.IntegerField(required=False)  # Output width
    height = forms.IntegerField(required=False)  # Output height

    uiw = forms.BooleanField(required=False)  # Use input width as width
    uih = forms.BooleanField(required=False)  # Use input height as height

    scale_width = forms.IntegerField(max_value=10, min_value=1, required=False)
    scale_height = forms.IntegerField(max_value=10, min_value=1, required=False)

    kar = forms.BooleanField(required=False)  # Keep Aspect Ratio
    foar = EnumChoiceField(required=False, choices=FOAR)  # Force Original Aspect Ratio

    def clean(self):
        kar = self.cleaned_data.get('kar')
        foar = self.cleaned_data.get('foar')
        uiw = self.cleaned_data.get('uiw')
        width = self.cleaned_data.get('width')
        uih = self.cleaned_data.get('uih')
        height = self.cleaned_data.get('height')

        if kar and foar != FOAR.Disable:
            raise forms.ValidationError("KAR and FOAR can not be set define at the same time")

        if not uiw and not width:
            raise forms.ValidationError("Please define width or uiw")

        if not uih and not height:
            raise forms.ValidationError("Please define height or uiw.")

        return super(ScaleFilter, self).clean()

    def generate(self, as_str: bool = True):
        self.validate()
        width = "iw" if self.cleaned_data['uiw'] else str(self.cleaned_data['width'])
        height = "ih" if self.cleaned_data['uih'] else str(self.cleaned_data['height'])

        scale_width = self.cleaned_data['scale_width']
        scale_height = self.cleaned_data['scale_height']

        width = width + "*" + str(scale_width) if scale_width else width
        height = height + "*" + str(scale_height) if scale_height else height

        height = "-1" if self.cleaned_data['kar'] else height

        scale = "scale=" + width + ":" + height

        if self.cleaned_data['foar'] != FOAR.Disable:
            scale = scale + ":force_original_aspect_ratio=" + str(self.cleaned_data['foar'])

        args = ["-filter:" + self.cleaned_data['stream'], scale]
        return " ".join(args) if as_str else args
