from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField, ValidationError, SelectField, IntegerField, IntegerRangeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, AnyOf, NumberRange

class StreamSettingsForm(FlaskForm):
    # TODO: change the default values to a function that gets the current settings
    framerate = IntegerField(label="Frame Rate", default=30) # an integer
    audio_delay = DecimalField(label="Audio Delay", places=1, default=0.3) # a float
    # TODO: implement a function that gets the resolutions available from the device using ffmpeg with ffmpeg  -hide_banner -f v4l2 -list_formats all -i /dev/video0
    resolution = SelectField(label="Resolution", choices=[(x, x) for x in ['1920x1080', '1600x1200', '1360x768', '1280x1024', '1280x960', '1280x720', '1024x768', '800x600', '720x576', '720x480', '640x480']], default='640x480')
    video_bitrate = IntegerRangeField("Video Bitrate (Kbps)", validators=[NumberRange(min=10_000, max=2_000_000)], default=90_000) # must be '50K' or '2M' something like that maybe a slider
    audio_bitrate = IntegerRangeField("Audio Bitrate (Kbps)", validators=[NumberRange(min=10_000, max=2_000_000)], default=7_000) # must be '50K' or '2M' something like that maybe a slider
    preset = SelectField(label="Preset", choices=[(x, x) for x in ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow', 'placebo']], default='ultrafast') 
    thread_queue_size = IntegerField(label="Thread Queue Size", validators=[AnyOf(values=[2**x for x in range(0, 14)], message="It must be a power of 2")], default=2048)     
    audio_codec = SelectField(label="Audio Codec", choices=[('aac', 'AAC'), ('g722', "G722"), ('g726le', 'G726'), ('libcodec2', 'Codec2'), ('libgsm', 'GSM') , ('libopus', 'Opus (libopus)'), ('opus', "Opus (opus)"), ('libvorbis', 'Vorvis')], default='libopus')
    video_codec = SelectField(label="Video Codec", choices=[('libaom-av1', 'AV1'), ('libx264', 'H.264'), ('mjpeg', 'MJPEG'), ('libvpx-vp9', 'VP9')], default='libx264')
    tune = SelectField(label="Tune", choices=['film', 'animation', 'grain', 'stillimage', 'fastdecode', 'zerolatency', 'psnr', 'ssim'], default='zerolatency') 
    # TODO: only show bitrate, vbr, and compression level when libopus is selected in audio_codec
    bitrate = IntegerField(label='Bitrate (bits/s)', default=1000) # maybe it works with libopus
    vbr = SelectField(label='Variable Bit Rate', choices=[('off', 'off'), ('on', 'on'), ('constrained', 'constrained')], default='off')
    compression_level = IntegerRangeField(label='Compression Level (0 is fast but low quality, 10 is high quality but slow)', validators=[NumberRange(min=0, max=10)], default=0)
    application = SelectField(label='Application', choices=[(x, x) for x in ['voip', 'audio', 'lowdelay']], default='lowdelay')
    apply_phase_inv = SelectField(label='Apply Phase Inversion', choices=[('1', 'Phase Inversion Enabled'), ('0', 'Phase Inversion Disabled')], default='0')
    sample_fmt = SelectField(label='Sample Format', choices=[(x, x) for x in ['u8', 's16', 's32', 'flt', 'dbl', 'u8p', 's16p', 's32p', 'fltp', 'dblp', 's64', 's64p']], default='s16')

    # Hls Settings
    # Size of the queue of outgoing packets. A higher value allows to increase throughput, a lower value allows to save RAM.
    writeQueueSize = IntegerField(label="Write Queue Size", validators=[AnyOf(values=[2**x for x in range(0, 14)], message="It must be a power of 2")], default=2048) 
    # Maximum size of outgoing UDP packets. This can be decreased to avoid fragmentation on networks with a low UDP MTU.
    udpMaxPayloadSize = IntegerField(label="UDP Max Payload Size", default=1472) 
    # Variant of the HLS protocol to use. Available options are:
    # * mpegts - uses MPEG-TS segments, for maximum compatibility.
    # * fmp4 - uses fragmented MP4 segments, more efficient.
    # * lowLatency - uses Low-Latency HLS.
    hlsVariant = SelectField(label="HLS Variant", choices=[(x, x) for x in ['lowLatency', 'mpegts', 'fmp4']], default='lowLatency') 
    # Number of HLS segments to keep on the server.
    # Segments allow to seek through the stream.
    # Their number doesn't influence latency.
    hlsSegmentCount = IntegerField(label="HLS Segment Count", default=7) 
    # Minimum duration of each segment.
    # A player usually puts 3 segments in a buffer before reproducing the stream.
    # The final segment duration is also influenced by the interval between IDR frames,
    # since the server changes the duration in order to include at least one IDR frame
    # in each segment.
    hlsSegmentDuration = StringField(label="HLS Segment Duration", default="1s")
    # Minimum duration of each part.
    # A player usually puts 3 parts in a buffer before reproducing the stream.
    # Parts are used in Low-Latency HLS in place of segments.
    # Part duration is influenced by the distance between video/audio samples
    # and is adjusted in order to produce segments with a similar duration.
    hlsPartDuration = StringField(label="HLS Part Duration", default="600ms")
    # Maximum size of each segment.
    # This prevents RAM exhaustion.
    hlsSegmentMaxSize = StringField(label="HLS Segment Max Size", default="50M")
    submit = SubmitField('Restart Stream')