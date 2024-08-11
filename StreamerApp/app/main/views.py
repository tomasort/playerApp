from flask import render_template, session, url_for, request, session, flash, jsonify, current_app
from flask_login import logout_user, login_required, current_user
from datetime import datetime
from ..models import User, Permission, Role
from .forms import StreamSettingsForm
from . import main
from .tasks import start_pipeline
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
    return "Hello world!"

@main.route('/button', methods=['POST'])
def button_pressed():
    button = request.form.get('button')
    command = ['/usr/bin/ir-ctl', '-K', button, '-k', '/remotes/fision.toml', '-d', '/dev/lirc0']
    button_press = subprocess.Popen(command)
    current_app.logger.info(f'The button {button} has been pressed and was executed with returncode: {button_press}')
    return "Button pressed successfully"

# TODO: implement the functionality of checking if the user has permission for contorlling the stream
@main.route('/stream-control', methods=['POST'])
def stream_control():
    action = request.form.get('action')
    if action == "start":
        pipeline_task_id = start_pipeline.delay(video_src=current_app.config['VIDEO_SOURCE'], audio_src=current_app.config['AUDIO_SOURCE'], webrtc_uri=current_app.config['WEBRTC_URI'])
        current_app.logger.info(f'The stream has been started')
    elif action == "stop":
        current_app.logger.info(f'The stream has been stopped')
    elif action == "restart":
        current_app.logger.info(f'The stream has been restarted')
    socketio.emit('status_update', {'status': 0})
    return ""

# TODO: implement this function so that it returns a page containing information about the user
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@socketio.on('connect')
def handle_connect():
    # Emit the initial status when a client connects
    socketio.emit('stream_status', {'status': 0})