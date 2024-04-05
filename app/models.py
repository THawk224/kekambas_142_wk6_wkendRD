from datetime import datetime, timezone, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='tasks')

    def __init__(self, title, description, user_id, completed=False, due_date=None):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.completed = completed
        self.due_date = due_date
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    tasks = db.relationship("Task", back_populates='author')
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone=True))

    def __init__(self, **kwargs ):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password',''))
        

    def __repr__(self):
        return f"<User {self.email}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.save()
    def check_password(self, plaintextpw):
        return check_password_hash(self.password, plaintextpw)
    def to_dict(self):
        return {'id': self.id,
                'firstname': self.first_name,
                'lastName': self.last_name,
                'username': self.username,
                'dateCreated': self.date_created
                }
    def get_token (self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}
    
    def update_user(self, **kwargs):
        allowed_fields = {"username", "password", "first_name", "last_name", "email"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()
        
    def delete_user(self):
        db.session.delete(self)
        db.session.commit()