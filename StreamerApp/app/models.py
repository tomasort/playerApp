from flask_login import UserMixin
from flask import current_app, request, url_for
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from datetime import datetime
from itsdangerous import TimedSerializer as Serializer


class StreamSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hls_errors_per_hour = db.Column(db.Integer)

    framerate = db.Column(db.Integer)
    audio_delay = db.Column(db.Float)
    resolution = db.Column(db.String(10))  
    video_bitrate = db.Column(db.Integer)
    audio_bitrate = db.Column(db.Integer)
    preset = db.Column(db.String(10))  
    thread_queue_size = db.Column(db.Integer)
    audio_codec = db.Column(db.String(10)) 
    video_codec = db.Column(db.String(10)) 
    tune = db.Column(db.String(12)) 
    bitrate = db.Column(db.Integer)
    vbr = db.Column(db.String(12)) 
    compression_level = db.Column(db.Integer)
    application = db.Column(db.String(10))
    apply_phase_inv = db.Column(db.String(1))
    sample_fmt = db.Column(db.String(5)) 
    writeQueueSize = db.Column(db.Integer)
    udpMaxPayloadSize = db.Column(db.Integer)
    hlsVariant = db.Column(db.String(20)) 
    hlsSegmentCount = db.Column(db.Integer)
    hlsSegmentDuration = db.Column(db.String(20))  
    hlsPartDuration = db.Column(db.String(20))  
    hlsSegmentMaxSize = db.Column(db.String(20))  


class Permission:
    WATCH = 1
    STREAM_CONTROL = 2
    ADMIN = 4


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Watcher': [Permission.WATCH],
            'User': [Permission.WATCH, Permission.STREAM_CONTROL],
            'Administrator': [Permission.WATCH, Permission.STREAM_CONTROL, Permission.ADMIN],
        }
        default_role = 'Watcher'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset': self.id})

    @staticmethod
    def reset_password(token, new_password, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email})

    def change_email(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'email': self.email,
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
        }
        return json_user
    
    def generate_auth_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    @staticmethod
    def verify_auth_token(token, expiration):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))