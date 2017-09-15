from django import forms
from django.utils.translation import ugettext_lazy as _

from .ffmpeg import FFMPEG_PATH
from .utils import BaseCommand, BaseFilter, EnumChoiceField
from .codecs import Codec
from .utils import LogLevel


class Command(BaseCommand):
    def __init__(self, **kwargs):
        self.args = []
        self.codecs = []
        self.filters = []
        super(Command, self).__init__(data=kwargs)

    # Main Options
    # -i
    input = forms.CharField(label=_("Input File Path"), required=True)
    output = forms.CharField(label=_("Output File Path"), required=True)

    # -loglevel
    loglevel = EnumChoiceField(choices=LogLevel, required=False, label=_("Log Level"))

    # -y : Overwrite output files without asking.
    overwrite = forms.NullBooleanField(required=False, label=_("Overwrite"))

    # -stream_loop
    # Set number of times input stream shall be looped. Loop 0 means no loop, loop -1 means infinite loop.
    stream_loop = forms.IntegerField(min_value=-1, required=False, label=_("Stream Loop"))

    # -t
    duration = forms.TimeField(label=_("I/O Duration"), required=False, input_formats=["%H:%M:%S.%f", "%H:%M:%S"])
    add_duration_before_input = forms.BooleanField(required=False, label=_("Add Duration Before Input Flag"))

    # -to
    to_position = forms.TimeField(label=_("Output Position"), required=False, input_formats=["%H:%M:%S.%f", "%H:%M:%S"])

    # -ss
    # When used as an input option (before -i), seeks in this input file to position.
    # Note that in most formats it is not possible to seek exactly, so ffmpeg will seek to the closest seek point
    # before position. When transcoding and -accurate_seek is enabled (the default),
    # this extra segment between the seek point and position will be decoded and discarded.
    # When doing stream copy or when -noaccurate_seek is used, it will be preserved.
    ss_position = forms.TimeField(label=_("I/O Position"), required=False, input_formats=["%H:%M:%S.%f", "%H:%M:%S"])
    add_ss_position_before_input = forms.BooleanField(label=_("Add I/O Position Before Input Flag"),
                                                      required=False)

    # -sseof
    # Like the -ss option but relative to the "end of file".
    # That is negative values are earlier in the file, 0 is at EOF.
    sseof_position = forms.TimeField(label=_("I/O Position (EOF)"), required=False,
                                     input_formats=["%H:%M:%S.%f", "%H:%M:%S"])

    # -fs
    # Set the file size limit, expressed in bytes. No further chunk of bytes is written after the limit is exceeded.
    # The size of the output file is slightly more than the requested file size.
    file_size_limit = forms.IntegerField(min_value=0, required=False, label=_("Output File Size Limit (as Bytes)"))

    # -itsoffset
    # Set the input time offset.
    # The offset is added to the timestamps of the input files. Specifying a positive offset means that
    # the corresponding streams are delayed by the time duration specified in offset.
    itsoffset = forms.TimeField(label=_("Input Time Offset"), required=False, input_formats=["%H:%M:%S.%f", "%H:%M:%S"])

    # -timestamp
    # Set the recording timestamp in the container.
    timestamp = forms.DateTimeField(required=False, label=_("Recording Timestamp"))
    timestamp_now = forms.BooleanField(required=False, label=_("Recording Timestamp: Auto Add Now"))

    # Video Options
    # -vn : Disable video recording.
    vn = forms.BooleanField(required=False, label=_("Disable Video Recording"))

    # -aspect
    # Set the video display aspect ratio specified by aspect.
    # aspect can be a floating point number string, or a string of the form num:den, where num and den are the numerator
    # and denominator of the aspect ratio. For example "4:3", "16:9", "1.3333", and "1.7777" are valid argument values.
    aspect = forms.DecimalField(required=False, label=_("Aspect Ratio"))

    # -c
    codecs = []

    # -filter
    filters = []

    def _add_filters(self):
        for flt in self.filters:
            self.args.append(flt.generate())

    def _add_codecs(self, before=False):
        for codec in self.codecs:
            if before == codec.cleaned_data['before_input']:
                self.args.append(codec.generate())

    def _add_aspect(self):
        self.args.append("-aspect")
        self.args.append(str(self.cleaned_data['aspect']))

    @staticmethod
    def _normalize(val: str):
        val = val.replace('"', '\\"')
        val = val.replace("'", "\\'")
        return val

    def _add_input_file(self):
        self.args.append("-i")
        self.args.append('"' + self._normalize(str(self.cleaned_data['input'])) + '"')

    def _add_log_level(self):
        self.args.append("-loglevel")
        self.args.append(str(self.cleaned_data['loglevel']))

    def _add_overwrite_or_not_existing_files(self):
        ow = self.cleaned_data['overwrite']
        if ow is None:
            return
        else:
            self.args.append('-y') if ow else self.args.append('-n')

    def _add_output_file(self):
        self.args.append('"' + self._normalize(str(self.cleaned_data['output'])) + '"')

    def _add_duration(self):
        self.args.append("-t")
        self.args.append(str(self.cleaned_data['duration']))

    def _add_file_size_limit(self):
        self.args.append("-fs")
        self.args.append(str(self.cleaned_data['file_size_limit']))

    def _add_ss_position(self):
        self.args.append("-ss")
        self.args.append(str(self.cleaned_data['ss_position']))

    def _add_to_position(self):
        self.args.append("-to")
        self.args.append(str(self.cleaned_data['to_position']))

    def _add_sseof_position(self):
        self.args.append("-sseof")
        self.args.append(str(self.cleaned_data['sseof_position']))

    def _add_stream_loop(self):
        self.args.append("-stream_loop")
        self.args.append(str(self.stream_loop))

    def _add_itsoffset(self):
        self.args.append("-itsoffset")
        self.args.append(str(self.cleaned_data['itsoffset']))

    def _add_timestamp(self, stamp):
        self.args.append("-timestamp")
        self.args.append(str(stamp))

    def _add_vn(self):
        self.args.append("-vn")

    def add_filter(self, flt: BaseFilter):
        """This will validate the filter and add to filters attribute"""
        flt.validate()
        self.filters.append(flt)
        return self

    def add_codec(self, codec: Codec):
        """This will validate the codec and add to codecs attribute"""
        codec.validate()
        self.codecs.append(codec)
        return self

    def generate(self, as_str: bool = True) -> str or []:
        """
        Generates FFmpeg command
        :param as_str: Return command as string else it will came as List
        :return: String or List
        """
        self.args = []
        self.args.append(FFMPEG_PATH)
        self.validate()

        # Before Input Tag
        if self.cleaned_data['loglevel']:
            self._add_log_level()

        if self.cleaned_data['add_duration_before_input']:
            self._add_duration()

        if self.cleaned_data['itsoffset']:
            self._add_itsoffset()

        if self.cleaned_data['stream_loop']:
            self._add_stream_loop()

        self._add_codecs(before=True)

        # Add Input File
        self._add_input_file()

        # After Input Tag
        self._add_overwrite_or_not_existing_files()

        if self.cleaned_data['duration']:
            self._add_duration()

        if self.cleaned_data['file_size_limit']:
            self._add_file_size_limit()

        if self.cleaned_data['to_position']:
            self._add_to_position()

        if self.cleaned_data['ss_position']:
            self._add_ss_position()

        if self.cleaned_data['sseof_position']:
            self._add_sseof_position()

        if self.cleaned_data['timestamp_now']:
            self._add_timestamp("now")
        elif self.cleaned_data['timestamp']:
            self._add_timestamp(self.cleaned_data['timestamp'])

        if self.cleaned_data['vn']:
            self._add_vn()

        if self.cleaned_data['aspect']:
            self._add_aspect()

        # Add Codecs
        self._add_codecs()

        # Add Filters
        self._add_filters()

        # Add Output File
        self._add_output_file()

        # Generate Command
        return " ".join(self.args) if as_str else self.args
