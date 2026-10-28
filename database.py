from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), default="Піца", nullable=False)
    description = db.Column(db.String(255))
    ingredients = db.Column(db.String(255))
    weight = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="нове")

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    guests_count = db.Column(db.Integer, nullable=False)
    reservation_time = db.Column(db.String(50), nullable=False)