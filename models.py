from django.db import models
from django.utils.translation import ugettext as _

from .utils.ffmpeg import FFMPEG_PATH
from .utils.main import LOG_LEVELS
from .utils.video import ASPECT_RATIOS


class BaseCommand(models.Model):
    def __init__(self, *args, **kwargs):
        self.command = []
        self.command.append(FFMPEG_PATH)
        super(BaseCommand, self).__init__(*args, **kwargs)

    # Main Options
    # -i
    input = models.CharField(verbose_name=_("Input File Path"))
    output = models.CharField(verbose_name=_("Output File Path"))

    # -loglevel
    log_level = models.CharField(max_length=7, choices=LOG_LEVELS, null=True, blank=True, verbose_name=_("Log Level"))

    # -y : Overwrite output files without asking.
    overwrite = models.BooleanField(default=True, verbose_name=_("Overwrite"))

    # -stream_loop
    # Set number of times input stream shall be looped. Loop 0 means no loop, loop -1 means infinite loop.
    stream_loop = models.SmallIntegerField(null=True, blank=True, verbose_name=_("Stream Loop"))

    # -t
    duration = models.TimeField(verbose_name=_("I/O Duration"), null=True, blank=True)
    add_duration_before_input = models.BooleanField(default=False, verbose_name=_("Add Duration Before Input Flag"))

    # -to
    to_position = models.TimeField(verbose_name=_("Output Position"), null=True, blank=True)

    # -ss
    # When used as an input option (before -i), seeks in this input file to position.
    # Note that in most formats it is not possible to seek exactly, so ffmpeg will seek to the closest seek point
    # before position. When transcoding and -accurate_seek is enabled (the default),
    # this extra segment between the seek point and position will be decoded and discarded.
    # When doing stream copy or when -noaccurate_seek is used, it will be preserved.
    ss_position = models.TimeField(verbose_name=_("I/O Position"), null=True, blank=True)
    add_ss_position_before_input = models.BooleanField(verbose_name=_("Add I/O Position Before Input Flag"),
                                                       default=False)

    # -sseof
    # Like the -ss option but relative to the "end of file".
    # That is negative values are earlier in the file, 0 is at EOF.
    sseof_position = models.TimeField(verbose_name=_("I/O Position (EOF)"), null=True, blank=True)

    # -fs
    # Set the file size limit, expressed in bytes. No further chunk of bytes is written after the limit is exceeded.
    # The size of the output file is slightly more than the requested file size.
    file_size_limit = models.BigIntegerField(null=True, blank=True, verbose_name=_("Output File Size Limit (as Bytes)"))

    # -itsoffset
    # Set the input time offset.
    # The offset is added to the timestamps of the input files. Specifying a positive offset means that
    # the corresponding streams are delayed by the time duration specified in offset.
    itsoffset = models.TimeField(verbose_name=_("Input Time Offset"), null=True, blank=True)

    # -timestamp
    # Set the recording timestamp in the container.
    timestamp = models.DateTimeField(null=True, blank=True, verbose_name=_("Recording Timestamp"))
    timestamp_now = models.BooleanField(default=False, verbose_name=_("Recording Timestamp: Auto Add Now"))

    # Video Options
    # -vn : Disable video recording.
    vn = models.BooleanField(default=False, verbose_name=_("Disable Video Recording"))

    # -aspect
    # Set the video display aspect ratio specified by aspect.
    # aspect can be a floating point number string, or a string of the form num:den, where num and den are the numerator
    # and denominator of the aspect ratio. For example "4:3", "16:9", "1.3333", and "1.7777" are valid argument values.
    aspect = models.DecimalField(null=True, blank=True, choices=ASPECT_RATIOS,
                                 verbose_name=_("Aspect Ratio"))

    vcodec = models.CharField

    @staticmethod
    def _get_io_path(obj):
        """Generates to file path for input or output fields"""
        if isinstance(obj, models.CharField) or isinstance(obj, models.URLField) or isinstance(obj, str):
            return str(obj)
        elif isinstance(obj, models.FileField) or isinstance(obj, models.ImageField):
            return str(obj.path)
        else:
            raise ValueError("Object type not suitable: %s" % type(obj))

    def _add_aspect(self):
        self.command.append("-aspect")
        self.command.append(str(self.aspect))

    def _add_input_file(self):
        self.command.append("-i")
        self.command.append(self._get_io_path(self.input))

    def _add_log_level(self):
        self.command.append("-loglevel")
        self.command.append(str(self.log_level))

    def _add_overwrite_or_not_existing_files(self):
        self.command.append('-y') if self.overwrite else self.command.append('-n')

    def _add_output_file(self):
        self.command.append(self._get_io_path(self.output))

    def _add_duration(self):
        self.command.append("-t")
        self.command.append(self.duration.strftime("%H:%M:%S.%f"))

    def _add_additional_kwargs(self, **kwargs):
        for key, value in kwargs:
            self.command.append(str(key))
            self.command.append(str(value))

    def _add_file_size_limit(self):
        self.command.append("-fs")
        self.command.append(str(self.file_size_limit))

    def _add_ss_position(self):
        self.command.append("-ss")
        self.command.append(self.ss_position.strftime("%H:%M:%S.%f"))

    def _add_to_position(self):
        self.command.append("-to")
        self.command.append(self.to_position.strftime("%H:%M:%S.%f"))

    def _add_sseof_position(self):
        self.command.append("-sseof")
        self.command.append(self.sseof_position.strftime("%H:%M:%S.%f"))

    def _add_stream_loop(self):
        self.command.append("-stream_loop")
        self.command.append(str(self.stream_loop))

    def _add_itsoffset(self):
        self.command.append("-itsoffset")
        self.command.append(self.itsoffset.strftime("%H:%M:%S.%f"))

    def _add_timestamp(self):
        self.command.append("-timestamp")
        self.command.append("now") if self.timestamp_now else self.command.append(str(self.timestamp))

    def _add_vn(self):
        self.command.append("-vn")

    def generate(self, as_string=False, **kwargs):
        """
        Generates FFmpeg command
        :param as_string: Return command as string
        :param kwargs: Additional arguments
        :return: String or Dict
        """

        # Before Input Tag
        if self.log_level:
            self._add_log_level()

        if self.add_duration_before_input:
            self._add_duration()

        if self.itsoffset:
            self._add_itsoffset()

        if self.stream_loop:
            self._add_stream_loop()

        # Add Input File
        self._add_input_file()

        # After Input Tag
        self._add_overwrite_or_not_existing_files()

        if self.duration:
            self._add_duration()

        if self.file_size_limit:
            self._add_file_size_limit()

        if self.to_position:
            self._add_to_position()

        if self.ss_position:
            self._add_ss_position()

        if self.sseof_position:
            self._add_sseof_position()

        if self.timestamp_now or self.timestamp:
            self._add_timestamp()

        if self.vn:
            self._add_vn()

        if self.aspect:
            self._add_aspect()

        # Add additional arguments
        if kwargs:
            self._add_additional_kwargs(**kwargs)

        # Add Output File
        self._add_output_file()

        # Generate Command
        return " ".join(self.command) if as_string else self.command
