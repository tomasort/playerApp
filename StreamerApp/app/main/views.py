from flask import render_template, session, url_for, request, session, flash, jsonify, current_app
from flask_login import logout_user, login_required, current_user
from datetime import datetime
from ..models import User, Permission, Role
from .forms import StreamSettingsForm
from . import main
from .. import db
from .. import moment
from .. import socketio 
import subprocess
import psutil
import signal
import json
import os


buttons = set(json.load(open('./app/static/buttons.json')))
# Initialize the FFmpeg process so that it can be closed later
STREAM_ACTIVE = "Active"
STREAM_STOPPED = "Stopped"

# TODO: store the stream status in the database? or in a file
stream_status = {'pid': None, 'status': STREAM_STOPPED}

def get_stream_status():
    if stream_status['pid'] is None:
        return STREAM_STOPPED
    return psutil.pid_exists(stream_status['pid'])

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

def start_stream(video_source, audio_source, framerate=30, audio_delay=0.3, resolution='640x480', video_bitrate='1000K', audio_bitrate='48K', preset="ultrafast", tune='zerolatency', sample_fmt="s16p", thread_queue_size=4096, vbr="on"):
    # restart_modules()
    itsoffset = [] 
    if audio_delay != 0:
        itsoffset = ['-itsoffset', str(audio_delay)]
    # start the stream using ffmpeg
    # TODO: figure out if mediamtx allos for upd input streams
    udp = ['-f',  'mpegts', 'udp://localhost:1234/mypath']
    rtsp = ['-f', 'rtsp', 'rtsp://localhost:8554/mystream?pkt_size=1028']

    # TODO: make the parameters of the command accessable through the frontend
    command = [
        '/usr/bin/ffmpeg', '-re',
        '-f', 'v4l2', '-thread_queue_size', str(thread_queue_size), '-framerate', str(framerate),  '-s', resolution, '-c:v', 'mjpeg', '-i', video_source,
        '-f', 'alsa', '-thread_queue_size', str(thread_queue_size),  *itsoffset, '-i', audio_source,
        # TODO: try to fix the audio issue in webrtc, I don't think it is because of this command, but somehting to do with mediamtx
        '-b:a', str(audio_bitrate), '-c:a', 'libopus', "-bufsize", "128M", "-vbr", str(vbr), "-ac", "1", "-sample_fmt", sample_fmt, "-payload_type", "111",
        '-b:v', str(video_bitrate), '-c:v', 'libx264', "-g", "25", '-flush_packets', '0',
        '-r', str(framerate), '-preset', preset, '-tune', tune,
        *rtsp
    ]
    print(" ".join(command))
    ffmpeg_process = subprocess.Popen(command, close_fds=True)
    stream_status['status'] = STREAM_ACTIVE
    

def stop_stream():
    def find_pid_by_name(process_name):
        pids = []
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                pids.append(process.info['pid'])
        return pids
    pids = find_pid_by_name("ffmpeg")
    if pids:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
    stream_status['status'] = STREAM_STOPPED
    # restart_modules()

def restart_stream(video_source, audio_source):
    stop_stream()
    start_stream(video_source, audio_source)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/webrtc')
def webrtc():
    return render_template('webrtc.html')

@main.route('/player', methods=['GET', 'POST'])
@login_required
def player():
    form = StreamSettingsForm()
    if form.validate_on_submit():
        print(form.data)
    return render_template('player.html', form=form)

@main.route('/set-settings', methods=['POST'])
@login_required
def set_settings():
    print(request.form)
    # TODO: stop the ffmpeg stream 
    # TODO: set the settings for HLS and mediamtx
    # TODO: set the settings for ffmpeg and start ffmpeg
    return "Hello world!"

# TODO: create a route that sets the stream settings to the default settings. Store the default settings in a file
    

@main.route('/button', methods=['POST'])
def button_pressed():
    button = request.form.get('button')
    remote = 'my_remote'
    remote2 = 'sony_fisionn'
    if button in buttons:
        print(button)
        command = ['/usr/bin/irsend', 'SEND_ONCE', remote, button, '-d', '/var/run/lirc/lirc1']
        button_press = subprocess.Popen(command)
        print(command, button_press.stdout)
    else:
        flash("The button is not valid")
    return ""

# TODO: implement the functionality of checking if the user has permission for contorlling the stream
@main.route('/stream-control', methods=['POST'])
def stream_control():
    action = request.form.get('action')
    video_source = current_app.config['VIDEO_SOURCE']
    audio_source = current_app.config['AUDIO_SOURCE']
    if action == "start":
        start_stream(video_source, audio_source)
    elif action == "stop":
        # stop the stream
        stop_stream()
    elif action == "restart":
        restart_stream(video_source, audio_source)
    else:
        flash("The action is not valid!")
    socketio.emit('status_update', {'status': stream_status['status']})
    return ""

@main.route('/hls-errors', methods=['POST'])
def hls_error_log():
    # TODO: log the error, the time, and the ffmpeg configuration, as well as the hls configurations to see which one gives bettter results. log it in an csv file. 
    pass


# TODO: implement this function so that it returns a page containing information about the user
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@socketio.on('connect')
def handle_connect():
    # Emit the initial status when a client connects
    socketio.emit('stream_status', {'status': stream_status['status']})