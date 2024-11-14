import streamlit as st
import pandas as pd
import re

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            background-color: #f4f7fc;
            padding: 2rem;
            border-radius: 10px;
        }
        .title {
            color: #4CAF50;
            font-size: 2.5rem;
            font-weight: bold;
        }
        .description {
            font-size: 1.25rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .ingredient-input {
            font-size: 1rem;
            padding: 10px;
            width: 100%;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        .recipe-card {
            background-color: #fff;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .recipe-title {
            color: #4CAF50;
            font-size: 1.75rem;
            font-weight: bold;
        }
        .missing-ingredients {
            color: #f44336;
        }
        .match-info {
            font-size: 1rem;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Display the title and description of the app in a styled layout
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.markdown("<h1 class='title'>Virtual Recipe Suggestion App</h1>", unsafe_allow_html=True)
st.markdown("<p class='description'>Find recipes based on the ingredients you have on hand!</p>", unsafe_allow_html=True)

# Get user input for ingredients with a more stylish input box
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):", key="ingredients", 
                                 placeholder="e.g., eggs, tomatoes, flour", 
                                 label_visibility="hidden", 
                                 help="Separate ingredients with commas.")

# Function to clean and format instructions
def clean_instructions(instruction_text):
    # Replace '|' with a period to act as a sentence delimiter
    instruction_text = instruction_text.replace('|', '.')
    instruction_text = re.sub(r'\.\.+', '.', instruction_text)  # Replace multiple dots with a single dot
    instruction_text = re.sub(r'\s+\.', '.', instruction_text)  # Remove space before periods
    instruction_text = re.sub(r'\.\s*', '. ', instruction_text)  # Ensure single space after each period

    # Capitalize the first letter of each sentence
    instruction_text = '. '.join(
        sentence.strip().capitalize() for sentence in instruction_text.split('. ')
    )

    return instruction_text.strip()

# Function to find recipes that match user's ingredients with at least 50% match
def find_matching_recipes(user_ingredients, df):
    matching_recipes = []
    for _, row in df.iterrows():
        # Ensure the ingredients field is a string before splitting
        if isinstance(row['ingredients'], str):
            recipe_ingredients = row['ingredients'].split("|")
            # Remove text within parentheses for each ingredient and convert to lowercase
            recipe_ingredients = [
                re.sub(r"\(.*?\)", "", ingredient).strip().lower()
                for ingredient in recipe_ingredients
            ]
        else:
            continue

        # Calculate matching ingredients
        matches = []
        for user_ingredient in user_ingredients:
            # Check if any recipe ingredient contains the user ingredient as a substring
            if any(user_ingredient in recipe_ingredient for recipe_ingredient in recipe_ingredients):
                matches.append(user_ingredient)

        match_count = len(matches)
        total_ingredients = len(recipe_ingredients)
        match_percentage = match_count / total_ingredients

        # Only include recipes with at least 50% matching ingredients
        if match_percentage >= 0.5:
            # Find missing ingredients more precisely
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

    # Sort recipes by the percentage of matching ingredients, descending
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

st.markdown("</div>", unsafe_allow_html=True)
