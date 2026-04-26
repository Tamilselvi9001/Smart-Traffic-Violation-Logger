from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Officer(UserMixin, db.Model):
    __tablename__ = 'officers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), default='Officer')

class Violation(db.Model):
    __tablename__ = 'violations'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    fine_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), default='Unpaid')
    qr_code_path = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_number': self.vehicle_number,
            'violation_type': self.violation_type,
            'location': self.location,
            'date': self.date.strftime('%Y-%m-%d'),
            'fine_amount': self.fine_amount,
            'status': self.status,
        }
