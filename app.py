import streamlit as st
import pandas as pd
import re

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Custom CSS for styling (with background GIF and borders around headings)
st.markdown("""
    <style>
        /* Set background GIF for the entire page */
        body {
            background: url('https://media.giphy.com/media/Buva2aomcuXBAD07PC/giphy.gif') no-repeat center center fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
        }
        /* Title styling with a border */
        .title {
            color: #4CAF50;
            font-size: 2.5rem;
            font-weight: bold;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.7);
        }
        /* Description styling */
        .description {
            font-size: 1.25rem;
            color: #ddd;
            margin-bottom: 2rem;
            text-align: center;
        }
        /* Ingredient input box styling */
        .ingredient-input {
            font-size: 1rem;
            padding: 10px;
            width: 100%;
            border-radius: 8px;
            border: 1px solid #ddd;
            margin-bottom: 1.5rem;
        }
        /* Recipe card styling */
        .recipe-card {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        /* Recipe title styling with a border */
        .recipe-title {
            color: #4CAF50;
            font-size: 1.75rem;
            font-weight: bold;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.7);
        }
        /* Missing ingredients text styling */
        .missing-ingredients {
            color: #f44336;
            font-weight: bold;
        }
        /* Match information styling */
        .match-info {
            font-size: 1rem;
            margin-top: 0.5rem;
            color: #555;
        }
    </style>
""", unsafe_allow_html=True)

# Display the title and description of the app in a styled layout
st.markdown("<h1 class='title'>Virtual Recipe Suggestion App</h1>", unsafe_allow_html=True)
st.markdown("<p class='description'>Find recipes based on the ingredients you have on hand!</p>", unsafe_allow_html=True)

# Get user input for ingredients with a more stylish input box
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):", key="ingredients", 
                                 placeholder="e.g., eggs, tomatoes, flour", 
                                 label_visibility="hidden", 
                                 help="Separate ingredients with commas.")

# Function to clean and format instructions
def clean_instructions(instruction_text):
    instruction_text = instruction_text.replace('|', '.')
    instruction_text = re.sub(r'\.\.+', '.', instruction_text)  # Replace multiple dots with a single dot
    instruction_text = re.sub(r'\s+\.', '.', instruction_text)  # Remove space before periods
    instruction_text = re.sub(r'\.\s*', '. ', instruction_text)  # Ensure single space after each period
    instruction_text = '. '.join(
        sentence.strip().capitalize() for sentence in instruction_text.split('. ')
    )

    return instruction_text.strip()

# Function to find recipes that match user's ingredients with at least 50% match
def find_matching_recipes(user_ingredients, df):
    matching_recipes = []
    for _, row in df.iterrows():
        if isinstance(row['ingredients'], str):
            recipe_ingredients = row['ingredients'].split("|")
            recipe_ingredients = [
                re.sub(r"\(.*?\)", "", ingredient).strip().lower()
                for ingredient in recipe_ingredients
            ]
        else:
            continue

        matches = []
        for user_ingredient in user_ingredients:
            if any(user_ingredient in recipe_ingredient for recipe_ingredient in recipe_ingredients):
                matches.append(user_ingredient)

        match_count = len(matches)
        total_ingredients = len(recipe_ingredients)
        match_percentage = match_count / total_ingredients

        if match_percentage >= 0.5:
            missing_ingredients = [
                recipe_ingredient for recipe_ingredient in recipe_ingredients
                if not any(user_ingredient in recipe_ingredient for user_ingredient in user_ingredients)
            ]
            matching_recipes.append({
                "title": row['recipe_title'],
                "match_count": match_count,
                "total_ingredients": total_ingredients,
                "match_percentage": match_percentage,
                "instructions": clean_instructions(row['instructions']),
                "url": row['url'],
                "missing_ingredients": missing_ingredients
            })

    matching_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return matching_recipes

# If the user inputs ingredients, display matching recipes
if user_ingredients:
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in user_ingredients.split(",")
    ]

    matching_recipes = find_matching_recipes(user_ingredients, df)
    
    if matching_recipes:
        for recipe in matching_recipes:
            st.markdown(f"<div class='recipe-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 class='recipe-title'><a href='{recipe['url']}' target='_blank'>{recipe['title']}</a></h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='match-info'>Matching Ingredients: {recipe['match_count']} / {recipe['total_ingredients']} ({recipe['match_percentage']:.0%})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='missing-ingredients'>Missing Ingredients: {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}</div>", unsafe_allow_html=True)
            st.markdown(f"<p><b>Instructions:</b><br>{recipe['instructions']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No matching recipes found. Try different ingredients.")
