import streamlit as st
import requests
import re
import streamlit.components.v1 as components

# API details
API_URL = "https://spoonacular.com/food-api"  # Replace with your API's endpoint
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your API key

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

    # Function to fetch recipes from the API
    def fetch_recipes(ingredients):
        params = {
            "ingredients": ",".join(ingredients),
            "api_key": API_KEY
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            return response.json()  # Assumes the API returns JSON data
        except requests.RequestException as e:
            st.error(f"Error fetching recipes: {e}")
            return []

    # Clean instructions text
    def clean_instructions(instruction_text):
        instruction_text = instruction_text.replace('|', '.')
        instruction_text = re.sub(r'\.\.+', '.', instruction_text)
        instruction_text = re.sub(r'\s+\.', '.', instruction_text)
        instruction_text = re.sub(r'\.\s*', '. ', instruction_text)
        instruction_text = '. '.join(
            sentence.strip().capitalize() for sentence in instruction_text.split('. ')
        )
        return instruction_text.strip()

    # Fetch recipes from the API
    recipes = fetch_recipes(user_ingredients)

    if recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in recipes:
            recipe_html = f"""
            <div class="recipe-card">
                <h3><a href="{recipe.get('url', '#')}" target="_blank">{recipe['title']}</a></h3>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="ingredient-list">Matching Ingredients:</span> {recipe.get('match_count', 'N/A')} / {recipe.get('total_ingredients', 'N/A')} 
                    <span class="match-percentage">({recipe.get('match_percentage', 0):.0%})</span>
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="missing-ingredients">Missing Ingredients:</span> {', '.join(recipe.get('missing_ingredients', [])) if recipe.get('missing_ingredients') else 'None'}
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;"><strong>Instructions:</strong> {clean_instructions(recipe.get('instructions', 'No instructions provided'))}</p>
            </div>
            """
            components.html(recipe_html, height=300)
    else:
        st.write("No matching recipes found. Try different ingredients.")
