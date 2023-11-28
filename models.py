from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from passlib.context import CryptContext


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='notes')

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', back_populates='user')  # Correct the relationship name
    contacts = db.relationship('Contact', backref='user')  # Add the correct relationship for contacts
    recipes = db.relationship('Recipe', backref='user')
    
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(255))
    # Add other recipe metadata fields here
    ingredients = db.relationship('Ingredient', backref='recipe', lazy='dynamic')
    instructions = db.relationship('Instruction', backref='recipe', lazy='dynamic')
    cooking_time = db.relationship('CookingTime', backref='recipe', uselist=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    ingredient_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    name = db.Column(db.String(255))
    unit = db.relationship('Unit', backref='ingredients')
    unit_id = db.Column(db.Integer, db.ForeignKey('units.unit_id'))
    amount = db.Column(db.Float)

class Unit(db.Model):
    __tablename__ = 'units'
    unit_id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(255))

class Instruction(db.Model):
    __tablename__ = 'instructions'
    instruction_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    step_text = db.Column(db.Text)

class CookingTime(db.Model):
    __tablename__ = 'cooking_times'
    cooking_time_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    time_in_minutes = db.Column(db.Integer)
