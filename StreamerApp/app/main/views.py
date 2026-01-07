from flask import render_template, session, url_for, request, session, flash, jsonify, current_app
from flask_login import logout_user, login_required, current_user
from datetime import datetime
from ..models import User, Permission, Role, PipelineSession
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
from celery import current_app as celery_app


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

def _create_pipeline_session():
    """Helper function to create a new pipeline session"""
    return PipelineSession(
        started_by=current_user.id,
        video_source=current_app.config.get('VIDEO_SOURCE'),
        audio_source=current_app.config.get('AUDIO_SOURCE'),
        webrtc_uri=current_app.config.get('WEBRTC_URI'),
        test_mode=not current_app.config.get('VIDEO_SOURCE')
    )


def _start_pipeline_task(session_record):
    """Helper function to start the pipeline task and update session"""
    # Start pipeline task
    task = start_pipeline.delay(
        video_src=current_app.config.get('VIDEO_SOURCE'),
        audio_src=current_app.config.get('AUDIO_SOURCE'),
        webrtc_uri=current_app.config.get('WEBRTC_URI')
    )
    
    # Update session with task ID
    session_record.task_id = task.id
    session_record.status = 'running'
    db.session.commit()
    
    return task


def _stop_active_session():
    """Helper function to stop the active session"""
    active_session = PipelineSession.get_active_session()
    if not active_session:
        return None
    
    # Revoke the Celery task
    try:
        celery_app.control.revoke(active_session.task_id, terminate=True)
    except Exception as e:
        current_app.logger.error(f'Error revoking task: {e}')
    
    # Update session record
    active_session.stop_session()
    current_app.logger.info(f'Pipeline stopped, task ID: {active_session.task_id}')
    
    return active_session


# TODO: implement the functionality of checking if the user has permission for controlling the stream
@main.route('/stream/start', methods=['POST'])
@login_required
def start_stream():
    # Check if already running
    active_session = PipelineSession.get_active_session()
    if active_session:
        return jsonify({'error': 'Pipeline already running'}), 400
    
    # Create new session record
    session_record = _create_pipeline_session()
    db.session.add(session_record)
    db.session.commit()
    
    # Start pipeline task
    task = _start_pipeline_task(session_record)
    
    current_app.logger.info(f'Pipeline started with task ID: {task.id}')
    
    socketio.emit('status_update', {'status': get_pipeline_status()})
    return jsonify({'success': True, 'message': 'Pipeline started', 'task_id': task.id})


@main.route('/stream/stop', methods=['POST'])
@login_required
def stop_stream():
    active_session = PipelineSession.get_active_session()
    if not active_session:
        return jsonify({'error': 'No active pipeline'}), 400
    
    stopped_session = _stop_active_session()
    
    socketio.emit('status_update', {'status': get_pipeline_status()})
    return jsonify({'success': True, 'message': 'Pipeline stopped', 'session_id': stopped_session.id})


@main.route('/stream/restart', methods=['POST'])
@login_required
def restart_stream():
    # Stop current session if exists
    active_session = PipelineSession.get_active_session()
    if active_session:
        _stop_active_session()
    
    # Start new session
    session_record = _create_pipeline_session()
    db.session.add(session_record)
    db.session.commit()
    
    # Start pipeline task
    task = _start_pipeline_task(session_record)
    
    current_app.logger.info(f'Pipeline restarted with task ID: {task.id}')
    
    socketio.emit('status_update', {'status': get_pipeline_status()})
    return jsonify({'success': True, 'message': 'Pipeline restarted', 'task_id': task.id})


@main.route('/stream/status', methods=['GET'])
def stream_status():
    """Get current stream status"""
    return jsonify(get_pipeline_status())


def get_pipeline_status():
    """Helper function to get current pipeline status"""
    active_session = PipelineSession.get_active_session()
    return {
        'is_running': active_session is not None,
        'session_id': active_session.id if active_session else None,
        'started_at': active_session.started_at.isoformat() if active_session else None,
        'started_by': active_session.user.username if active_session else None
    }


# TODO: implement this function so that it returns a page containing information about the user
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@socketio.on('connect')
def handle_connect():
    # Emit the initial status when a client connects
    socketio.emit('stream_status', {'status': 0})