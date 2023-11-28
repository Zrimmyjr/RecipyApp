from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from website.auth import login, logout
from .models import Note, Contact, Recipe, Ingredient, Instruction, Unit, CookingTime
from . import db
import re
import json
import os
import openai

from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')

openai.api_key = OPENAI_KEY

views = Blueprint('views', __name__)
@views.route('/send-to-chatGPT', methods=['POST'])
def send_to_chatGPT(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        #Controls how many bytes of text
        max_tokens=3500,
        n=1,
        stop=None,
        #How creative it can be
        temperature=0.1,
        )
    if isinstance(response, str):
        return response
    elif isinstance(response, dict):
        return response['choices'][0]['message']['content']
    else:
        # Handle other cases if necessary
        return None  # Adjust this as needed

def create_note(note_data):
    new_note = Note(data=note_data, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    flash('Ingredients added!', category='success')
    
def create_recipe_from_gpt_response(response):
    try:
         response_data = json.loads(response)
         if isinstance(response_data, dict) and all(key in response_data for key in ['recipe_name', 'ingredients', 'instructions', 'time_to_cook']):
            recipe = Recipe(recipe_name=response_data['recipe_name'], user_id=current_user.id)
            
            # Create and add Ingredients
            ingredients = response_data['ingredients']
            for ingredient_data in ingredients:
                unit_name = ingredient_data['unit']
                unit = Unit.query.filter_by(unit_name=unit_name).first()
                if not unit:
                    unit = Unit(unit_name=unit_name)
                    db.session.add(unit)

                ingredient = Ingredient(
                    name=ingredient_data['name'],
                    unit=unit,
                    amount=ingredient_data['amount']
                )
                recipe.ingredients.append(ingredient)

            # Create and add Instructions
            instructions = response_data['instructions']
            for step_text in instructions:
                instruction = Instruction(step_text=step_text)
                recipe.instructions.append(instruction)

            # Create CookingTime
            cooking_time = CookingTime(time_in_minutes=response_data['time_to_cook'])
            recipe.cooking_time = cooking_time

            # Add the Recipe instance to the session and commit
            db.session.add(recipe)
            db.session.commit()
            flash('Recipe Generated!', category='success')
         else:
            flash('Invalid response format', category='error')
    except json.JSONDecodeError:
        flash('Invalid JSON response', category='error')
    
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        cuisine = request.form.get('cuisine')
        
        if len(note) < 2:
            flash('Enter in at least one ingredient!', category='error')
        elif not re.match("^[a-zA-Z, ]+$", note):
                flash('Ingredients must contain only letters!', category='error')
        else:
            create_note(note)
            gpt_in_progress = True
            schema = {
                        "type": "object",
                        "properties": {
                            "recipe_name": { "type": "string" },
                            "ingredients": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": { "type": "string" },
                                        "unit": { 
                                            "type": "string",
                                            "enum": ["grams", "ml", "cups", "teaspoons", ""]
                                        },
                                        "amount": { "type": "number" }
                                    },
                                    "required": ["name", "unit", "amount"]
                                }
                            },
                            "instructions": {
                                "type": "array",
                                "description": "Steps to prepare the recipe (no numbering)",
                                "items": { "type": "string" }
                            },
                            "time_to_cook": {
                                "type": "number",
                                "description": "Total time to prepare the recipe in minutes"
                            }
                        },
                        "required": ["recipe_name", "ingredients", "instructions", "time_to_cook"]
                    }
            new_note = f"Provide me recipes I could make with these ingredients in {str(cuisine)} style cuisine: {note} only respond with one entry using the provided json schema {schema}"
            messages=([{"role": "user", "content": new_note}])
            response = send_to_chatGPT(messages)
            create_recipe_from_gpt_response(response)
    return render_template("home.html", user=current_user)
@views.route('/about', methods=['GET'])
def about():
    if request.method == 'GET':
        return render_template("about.html", user=current_user)

@views.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        contact = request.form.get('contact')
        new_contact = Contact(data=contact, user_id=current_user.id)
        db.session.add(new_contact)
        db.session.commit()
        flash('Message Sent!', category='success')
    return render_template("contact.html", user=current_user)
               
@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete_recipe', methods=['POST'])
def delete_recipe():  
    recipe = json.loads(request.data)
    recipe_id = recipe['recipe_id']
    if recipe_id is None:
        return jsonify({"error": "Recipe ID is missing"}), 400

    # Check if the recipe with the provided ID exists
    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404

    try:
        # Delete the recipe
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the recipe"}), 500