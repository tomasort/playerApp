from flask import render_template, session, url_for, request, session
from flask_login import logout_user, login_required
from ..models import User
from . import main
from .. import db
import subprocess
import psutil
import signal
import json
import os


buttons = set(json.load(open('./app/static/buttons.json')))
# Initialize the FFmpeg process so that it can be closed later
ffmpeg_process = None

def find_pid_by_name(process_name):
    pids = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            pids.append(process.info['pid'])
    return pids

def restart_modules():
    # This commands can change if you use another OS
    sudo_command = '/usr/bin/sudo'
    sh_command = '/usr/bin/sh'
    modprobe_command = '/usr/sbin/modprobe'
    echo_command = '/usr/bin/echo'
    # reload the required modules before starting the stream. This is to avoid problems with ffmpeg (I think it is because of the capture card that I'm using)
    command = f"{sudo_command} {sh_command} -c '{modprobe_command} -v -r uvcvideo && {modprobe_command} -v uvcvideo'"
    password = os.getenv('ODROID_PASSWORD')
    os.system('{} {} | {} -S {}'.format(echo_command, password, sudo_command, command))

def start_stream():
    global ffmpeg_process
    restart_modules()
    # start the stream using ffmpeg
    print("Starting the stream!")
    # audio_device = "hw:CARD=Capture,DEV=0"
    audio_device = "hw:CARD=MS2109,DEV=0"
    framerate = 30
    audio_delay = 0.3  # https://trac.ffmpeg.org/wiki/UnderstandingItsoffset
    itsoffset = [] 
    if audio_delay != 0:
        itsoffset = ['-itsoffset', str(audio_delay)]
    command = [
        '/usr/bin/ffmpeg', '-f', 'v4l2', '-thread_queue_size', '1024', '-framerate', str(framerate), '-s', '720x480', '-c:v', 'mjpeg', '-i', '/dev/video0',
        '-f', 'alsa', '-ac', '2', '-thread_queue_size', '1024', *itsoffset, '-i', audio_device,
        '-b:a', '192k', '-c:a', 'aac', '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency', 
        '-f', 'flv', 'rtmp://localhost/live/stream'
    ]
    ffmpeg_process = subprocess.Popen(command, close_fds=True)

def stop_stream():
    global ffmpeg_process
    print("Stopping the stream!")
    pids = find_pid_by_name("ffmpeg")
    if pids:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
    restart_modules()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/player')
def player():
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
