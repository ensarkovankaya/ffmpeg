# FFmpeg Command Generator

Generates ffmpeg commands programmatically with python.

## Requirements
	- Django
	- Ffmpeg

## Example: Generating 10 Minute Video
```
from ffmpeg.generator import Command
from ffmpeg.utils.codecs import Codec
from ffmpeg.utils.filters import StreamSpecifier
import subprocess

# Generating 10 Minute Video from Another Video
input = "input.mp4"
output = "output.mp4"
duration = "00:10:00"  # 10 minutes

cmd = Command(data={'input': input, 'output': output, 'duration': duration})

# Copy the input video codec
codec = Codec(data={"copy": True, "stream": StreamSpecifier.Video})
cmd.add_codec(codec)

cmd.generate(as_string=True) # Returns as string
"/usr/bin/ffmpeg -i input.mp4 -t 00:10:00 -c:v copy output.mp4"

# Run command
ps = subprocess.run(cmd.generate(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
```

## Example: Scaling Video
```
from ffmpeg.generator import Command
from ffmpeg.utils.codecs import Codec
from ffmpeg.utils.filters import StreamSpecifier, ScaleFilter, FOAR
import subprocess

# Generating 10 Minute Video from Another Video
input = "input.mp4"
output = "output.mp4"

cmd = Command(data={'input': input, 'output': output})

# Scale to : 1920x1080
scale = ScaleFilter(data={"width": 1920, "height": 1080, "foar": FOAR.Decrease})
cmd.add_filter(scale)

cmd.generate(as_string=True) # Returns as string
"/usr/bin/ffmpeg -i input.mp4 -filter:v scale=1920x1080:force_original_aspect_ratio=decrease output.mp4"

# Run command
ps = subprocess.run(cmd.generate(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
```

## Settings

* FFMPEG_PATH (Optional)
    
    Program path. Module will try to find itself by asking the system.

    ```# Default: "/usr/bin/ffmpeg"```
    

* FFMPEG_LOG_LEVELS (Optional)

    For the Admin panel you can simplify it.

    ```
    # Defaults: 
    [("quiet", _("Quite")),
    ("panic", _("Panic")),
    ("fatal", _("Fatal")),
    ("error", _("Error")),
    ("warning", _("Warning")),
    ("info", _("Info")),
    ("verbose", _("Verbose")),
    ("debug", _("Debug")),
    ("trace", _("Trace"))]
    ```

* FFMPEG_ASPECT_RATIOS (Optional):

    ```
    # Defaults:
    [(None, _("Not Specified")),
    (4 / 3, "4:3"),
    (16 / 9, "16:9")]
    ```

* FFMPEG_VIDEO_SIZES (Optional)

    https://ffmpeg.org/ffmpeg-utils.html#Video-size
    
    ```
    # Defaults:
    [(None, _("Not Specified")), ('720x480', 'NTSC 720x480'), ('720x576', 'PAL 720x576'),
    ('352x240', 'QNTSC 352x240'), ('352x288', 'QPAL 352x288'), ('640x480', 'SNTSC 640x480'),
    ('768x576', 'SPAL 768x576'), ('352x240', 'FILM 352x240'), ('352x240', 'NTSC-FILM 352x240'),
    ('128x96', 'SQCIF 128x96'), ('176x144', 'QCIF 176x144'), ('352x288', 'CIF 352x288'),
    ('704x576', '4CIF 704x576'), ('1408x1152', '16CIF 1408x1152'), ('160x120', 'QQVGA 160x120'),
    ('320x240', 'QVGA 320x240'), ('640x480', 'VGA 640x480'), ('800x600', 'SVGA 800x600'),
    ('1024x768', 'XGA 1024x768'), ('1600x1200', 'UXGA 1600x1200'), ('2048x1536', 'QXGA 2048x1536'),
    ('1280x1024', 'SXGA 1280x1024'), ('2560x2048', 'QSXGA 2560x2048'),
    ('5120x4096', 'HSXGA 5120x4096'), ('852x480', 'WVGA 852x480'), ('1366x768', 'WXGA 1366x768'),
    ('1600x1024', 'WSXGA 1600x1024'), ('1920x1200', 'WUXGA 1920x1200'),
    ('2560x1600', 'WOXGA 2560x1600'), ('3200x2048', 'WQSXGA 3200x2048'),
    ('3840x2400', 'WQUXGA 3840x2400'), ('6400x4096', 'WHSXGA 6400x4096'),
    ('7680x4800', 'WHUXGA 7680x4800'), ('320x200', 'CGA 320x200'), ('640x350', 'EGA 640x350'),
    ('852x480', 'HD480 852x480'), ('1280x720', 'HD720 1280x720'), ('1920x1080', 'HD1080 1920x1080'),
    ('2048x1080', '2K 2048x1080'), ('1998x1080', '2KFLAT 1998x1080'),
    ('2048x858', '2KSCOPE 2048x858'), ('4096x2160', '4K 4096x2160'),
    ('3996x2160', '4KFLAT 3996x2160'), ('4096x1716', '4KSCOPE 4096x1716'),
    ('640x360', 'NHD 640x360'), ('240x160', 'HQVGA 240x160'), ('400x240', 'WQVGA 400x240'),
    ('432x240', 'FWQVGA 432x240'), ('480x320', 'HVGA 480x320'), ('960x540', 'QHD 960x540'),
    ('2048x1080', '2KDCI 2048x1080'), ('4096x2160', '4KDCI 4096x2160'),
    ('3840x2160', 'UHD2160 3840x2160'), ('7680x4320', 'UHD4320 7680x4320')]
    ```

* FFMPEG_VIDEO_RATES (Optional)
    
    https://ffmpeg.org/ffmpeg-utils.html#Video-rate
    
    ```
    # Defaults
    [(None, _("Not Specified")), ('ntsc', 'NTSC 30000/1001'), ('pal', 'PAL 25/1'),
    ('qntsc', 'QNTSC 30000/1001'), ('qpal', 'QPAL 25/1'), ('sntsc', 'SNTSC 30000/1001'),
    ('spal', 'SPAL 25/1'), ('film', 'FILM 24/1'), ('ntsc-film', 'NTSC-FILM 24000/1001')]
    ```