from flask import render_template, session, url_for, request, session
from flask_login import logout_user, login_required
from ..models import User
from . import main
from .. import db
import subprocess
import psutil
import signal
import os

buttons = {
    'KEY_0',
    'KEY_1',
    'KEY_2',
    'KEY_3',
    'KEY_4',
    'KEY_5',
    'KEY_6',
    'KEY_7',
    'KEY_8',
    'KEY_9',
    'KEY_NUMERIC_POUND',
    'KEY_NUMERIC_STAR',
    'KEY_PHONE',		# THIS ONE IS NOT WORKING!
    'KEY_FAVORITES',		# ALSO NOT WORKING
    'KEY_OPTION',
    'KEY_A',			# NOT WORKING
    'KEY_B',			# NOT WORKING
    'KEY_C',			# NOT WORKING
    'KEY_GOTO',			# GO
    'KEY_LEFT',
    'KEY_RIGHT',
    'KEY_UP',
    'KEY_DOWN',
    'KEY_D',			# ON DEMAND
    'KEY_G',			# GUIDE
    'KEY_MENU',
    'KEY_PAGEDOWN',		# DAY -
    'KEY_PAGEUP',		# DAY +
    'KEY_ENTER',			# Also OK
    'KEY_BACK',
    'KEY_EXIT',
    'KEY_PAUSE',
    'KEY_PLAY',
    'KEY_FASTFORWARD',
    'KEY_FASTREVERSE',
    'KEY_RECORD',
    'KEY_RESTART',		# the square button
    'KEY_FRAMEBACK',
    'KEY_FRAMEFORWARD',	# The arrow with the line at the end
    'KEY_CHANNELDOWN',
    'KEY_CHANNELUP',
    'KEY_ZOOMIN',		# ZOOM
    'KEY_PROGRAM',		# LIVE TV
    'KEY_PVR',			# DVR
    'KEY_INFO',
    'KEY_LAST',
    'KEY_POWER',
}

# Initialize the FFmpeg process
ffmpeg_process = None

def find_pid_by_name(process_name):
    pids = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            pids.append(process.info['pid'])
    return pids

def restart_modules():
    # reload the required modules before starting the stream. This is just to avoid any problems
    command = "/usr/bin/sudo /bin/sh -c '/sbin/modprobe -v -r uvcvideo && /sbin/modprobe -v uvcvideo'"
    password = os.getenv('ODROID_PASSWORD')
    os.system('/bin/echo {} | /usr/bin/sudo -S {}'.format(password, command))


def start_stream():
    global ffmpeg_process
    restart_modules()
    # start the stream using ffmpeg
    print("Starting the stream!")
    audio_device = "hw:CARD=Capture,DEV=0"
    framerate = 30
    # https://trac.ffmpeg.org/wiki/UnderstandingItsoffset
    audio_delay = 0.3
    itsoffset = [] 
    if audio_delay != 0:
        itsoffset = ['-itsoffset', str(audio_delay)]
    command = [
        '/usr/bin/ffmpeg', '-f', 'v4l2', '-framerate', str(framerate), '-s', '720x480', '-c:v', 'mjpeg', '-i', '/dev/video0',
        '-f', 'alsa', '-ac', '2', *itsoffset, '-i', audio_device,
        '-b:a', '192k', '-c:a', 'aac', '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency', 
        '-f', 'flv', 'rtmp://localhost/live/stream'
    ]
    ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ffmpeg_process.stderr.readline()
    print(output.strip())

def stop_stream():
    global ffmpeg_process
    print("Stopping the stream!")
    pids = find_pid_by_name("ffmpeg")
    if ffmpeg_process:
        ffmpeg_process.send_signal(signal.SIGINT)
        ffmpeg_process.wait()
        ffmpeg_process = None
    elif pids:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
    restart_modules()

@main.route('/')
def index():
    return "Hello user, this is the player app"

@main.route('/player')
def hello():
    return render_template('player.html')

@main.route('/button', methods=['POST'])
def button_pressed():
    button = request.form.get('button')
    if button in buttons:
        print(button)
        command = ['/usr/bin/irsend', 'SEND_ONCE', 'my_remote', button, '-d', '/var/run/lirc/lirc1']
        button_press = subprocess.Popen(command)
    else:
        print("The button is not valid")
    return ""


@main.route('/stream-control', methods=['POST'])
def stream_control():
    action = request.form.get('action')
    if action == "start":
        start_stream()
    elif action == "stop":
        # stop the stream
        stop_stream()
    elif action == "restart":
        stop_stream()
        start_stream()
    else:
        print("The action is not valid!")
    return ""
