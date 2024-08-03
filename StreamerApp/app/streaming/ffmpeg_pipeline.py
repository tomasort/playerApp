import subprocess
import psutil
from .media_pipeline import MediaPipeline

def restart_modules():
    """
    Reloads the required modules before starting the stream to avoid issues with ffmpeg.

    The commands used are specific to Unix-like operating systems and may need to be adjusted for other OSes.
    """
    # This commands can change if you use another OS
    sudo_command = '/usr/bin/sudo'
    sh_command = '/usr/bin/sh'
    modprobe_command = '/usr/sbin/modprobe'
    echo_command = '/usr/bin/echo'
    # reload the required modules before starting the stream. This is to avoid problems with ffmpeg (I think it is because of the capture card that I'm using)
    command = f"{sudo_command} {sh_command} -c '{modprobe_command} -v -r uvcvideo && {modprobe_command} -v uvcvideo'"
    password = os.getenv('ODROID_PASSWORD')
    os.system('{} {} | {} -S {}'.format(echo_command, password, sudo_command, command))

def find_pid_by_name(process_name):
    """
    Finds process IDs by process name.

    Args:
        process_name (str): Name of the process to find.

    Returns:
        list: List of process IDs that match the given process name.
    """
    pids = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            pids.append(process.info['pid'])
    return pids

class FFmpegPipeline(MediaPipeline):
    """
    FFmpeg-based media pipeline for handling video and audio streams.

    Attributes:
        process (subprocess.Popen): Subprocess for running the ffmpeg command.
        pid (int): Process ID of the running ffmpeg process.
        framerate (str): Framerate of the video stream.
        audio_delay (float): Audio delay in seconds.
        resolution (str): Resolution of the video stream.
        video_bitrate (str): Video bitrate.
        audio_bitrate (str): Audio bitrate.
        preset (str): FFmpeg preset.
        tune (str): FFmpeg tune option.
        sample_fmt (str): Audio sample format.
        thread_queue_size (str): Thread queue size for ffmpeg.
        vbr (str): Variable bitrate setting for audio.
    """

    def __init__(self, v_src: str, a_src: str):
        super().__init__(v_src, a_src)
        self.process = None
        self.pid = None
        self.framerate = '30'
        self.audio_delay = 0.3
        self.resolution = '640x480'
        self.video_bitrate = '1000K' 
        self.audio_bitrate = '48K'
        self.preset = 'ultrafast'
        self.tune='zerolatency'
        self.sample_fmt = 's16p'
        self.thread_queue_size='4096'
        self.vbr = "on"

    def start(self):
        """
        Starts the ffmpeg process to handle video and audio streams.
        """
        itsoffset = [] 
        if self.audio_delay != 0:
            itsoffset = ['-itsoffset', str(self.audio_delay)]
        udp = ['-f',  'mpegts', 'udp://localhost:1234/mypath']
        rtsp = ['-f', 'rtsp', 'rtsp://localhost:8554/mystream?pkt_size=1028']
        command = [
            '/usr/bin/ffmpeg', '-re',
            '-f', 'v4l2', '-thread_queue_size', self.thread_queue_size, '-framerate', self.framerate,  '-s', self.resolution, '-c:v', 'mjpeg', '-i', self.v_src,
            '-f', 'alsa', '-thread_queue_size', self.thread_queue_size,  *itsoffset, '-i', self.a_src,
            '-b:a', self.audio_bitrate, '-c:a', 'libopus', "-bufsize", "128M", "-vbr", self.vbr, "-ac", "1", "-sample_fmt", self.sample_fmt, "-payload_type", "111",
            '-b:v', self.video_bitrate, '-c:v', 'libx264', "-g", "25", '-flush_packets', '0',
            '-r', self.framerate, '-preset', self.preset, '-tune', self.tune,
            *rtsp
        ]
        self.process = subprocess.Popen(command, close_fds=True)
        self.pid = self.process.pid

    def stop(self):
        """
        Stops the ffmpeg process if it is running.
        """
        pids = find_pid_by_name("ffmpeg")
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
        # We might have to restart the module uvcvideo for the next time we start the stream

    def get_status(self):
        """
        Gets the current status of the ffmpeg process.

        Returns:
            int: 0 if the process is not running, 1 if it is running.
        """
        if self.pid is None:
            return 0
        return 1 if psutil.pid_exists(self.pid) else 0