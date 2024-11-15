import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Display the title and description of the app with emoji
st.title("🍲 Virtual Recipe Suggestion App")
st.markdown(
    """
    <p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
        Find recipes based on the ingredients you have on hand! 🍳
    </p>
    """,
    unsafe_allow_html=True,
)

# Add styling for all body text, cards, and recipe elements
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f8f4;
            color: #333;
        }
        .recipe-card {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-size: 1.1em;
        }
        .recipe-card a {
            text-decoration: none;
            color: #d97706;
            font-size: 1.2em;
            font-weight: bold;
        }
        .recipe-card a:hover {
            text-decoration: underline;
        }
        .recipe-card p {
            color: #555;
        }
        .header {
            text-align: center;
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 20px;
        }
        .ingredient-list {
            color: #3c763d;
            font-weight: bold;
        }
        .match-percentage {
            color: #5bc0de;
        }
        .missing-ingredients {
            color: #d9534f;
        }
        .input-box {
            width: 100%;
            padding: 10px;
            font-size: 1.1em;
            border-radius: 8px;
            border: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .input-box:focus {
            border-color: #3c763d;
            outline: none;
        }
    </style>
""", unsafe_allow_html=True)

# Get user input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    key="ingredients_input",
    placeholder="e.g., oil, rice, salt",
    help="Type ingredients you have at home to find recipes.",
    max_chars=200,
    label_visibility="visible",
)

if user_ingredients:
    # Convert user input to a cleaned list of ingredients
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in re.split(r",\s*|,\s*", user_ingredients)  # Split on commas and handle extra spaces
        if ingredient.strip()  # Ignore empty entries
    ]

    # Function to clean and format instructions
    def clean_instructions(instruction_text):
        instruction_text = instruction_text.replace('|', '.')
        instruction_text = re.sub(r'\.\.+', '.', instruction_text)
        instruction_text = re.sub(r'\s+\.', '.', instruction_text)
        instruction_text = re.sub(r'\.\s*', '. ', instruction_text)

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

    # Find recipes and display them with custom HTML
    matching_recipes = find_matching_recipes(user_ingredients, df)
    
    if matching_recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in matching_recipes:
            recipe_html = f"""
            <div class="recipe-card">
                <h3><a href="{recipe['url']}" target="_blank">{recipe['title']}</a></h3>
                <p style="color: #4b9e47; font-size: 1.1em;"><span class="ingredient-list">Matching Ingredients:</span> {recipe['match_count']} / {recipe['total_ingredients']} 
                <span class="match-percentage">({recipe['match_percentage']:.0%})</span></p>
                <p style="color: #4b9e47; font-size: 1.1em;"><span class="missing-ingredients">Missing Ingredients:</span> {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}</p>
                <p style="color: #4b9e47; font-size: 1.1em;"><strong>Instructions:</strong> {recipe['instructions']}</p>
            </div>
            """
            components.html(recipe_html, height=300)
    else:
        st.write("No matching recipes found. Try different ingredients.")
