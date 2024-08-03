from flask import render_template, session, url_for, request, session, flash, jsonify, current_app
from flask_login import logout_user, login_required, current_user
from datetime import datetime
from ..models import User, Permission, Role
from .forms import StreamSettingsForm
from . import main
from .. import db
from .. import buttons 
from .. import moment
from .. import socketio 
import subprocess
import psutil
import signal
import os


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/webrtc')
def webrtc():
    return render_template('webrtc.html')
    # return render_template('webrtc.html')

@main.route('/player', methods=['GET', 'POST'])
def player():
    form = StreamSettingsForm()
    if form.validate_on_submit():
        print(form.data)
    return render_template('player.html', form=form)

@main.route('/set-settings', methods=['POST'])
@login_required
def set_settings():
    print(request.form)
    # TODO: set the settings for HLS and mediamtx
    # TODO: set the settings for ffmpeg and start ffmpeg
    return "Hello world!"

# TODO: create a route that sets the stream settings to the default settings. Store the default settings in a file

@main.route('/button', methods=['POST'])
def button_pressed():
    button = request.form.get('button')
    command = ['/usr/bin/ir-ctl', '-K', button, '-k', '/remotes/fision.toml', '-d', '/dev/lirc0']
    button_press = subprocess.Popen(command)

# TODO: implement the functionality of checking if the user has permission for contorlling the stream
@main.route('/stream-control', methods=['POST'])
def stream_control():
    action = request.form.get('action')
    if action == "start":
        current_app.pipeline.set_video_source('/dev/video1')
        current_app.pipeline.set_audio_source('hw:0,0')
        current_app.pipeline.start()
    elif action == "stop":
        current_app.pipeline.stop()
    elif action == "restart":
        current_app.pipeline.restat()
    else:
        flash("The action is not valid!")
    socketio.emit('status_update', {'status': current_app.pipeline.get_status()})
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
    socketio.emit('stream_status', {'status': current_app.pipeline.get_status()})