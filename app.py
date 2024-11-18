import streamlit as st
import requests
import re
import openai
import streamlit.components.v1 as components

# Spoonacular API details
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_API_KEY = "25d917fef9554ad3b05f732cd181a39f"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# App UI
st.title("🍲 Virtual Recipe Suggestion App")
st.markdown(
    """
    <p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
        Find recipes based on the ingredients you have on hand! 🍳
    </p>
    """,
    unsafe_allow_html=True,
)

# Styling
st.markdown(
    """
    <style>
        .recipe-card { background-color: #fff; padding: 20px; margin-bottom: 20px; border-radius: 10px; }
        .recipe-card img { width: 100%; border-radius: 10px; margin-bottom: 10px; }
        .recipe-card a { text-decoration: none; color: #d97706; font-weight: bold; }
        .recipe-card a:hover { text-decoration: underline; }
        .ingredient-list { color: #3c763d; font-weight: bold; }
        .missing-ingredients { color: #d9534f; }
        .match-percentage { color: #5bc0de; }
    </style>
    """,
    unsafe_allow_html=True,
)

# User input
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Chicken, Rice, Broccoli",
)

preferences = st.text_input("Enter dietary preferences (optional, e.g., vegan, gluten-free):")

# Functions
def fetch_recipes(ingredients):
    """Fetch recipes from Spoonacular API."""
    params = {
        "ingredients": ",".join(ingredients),
        "apiKey": SPOONACULAR_API_KEY,
        "number": 50,
        "ranking": 1,
    }
    try:
        response = requests.get(SPOONACULAR_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching recipes: {e}")
        return []

def suggest_substitutes(missing_ingredients):
    """Suggest ingredient substitutions using OpenAI."""
    if not missing_ingredients:
        return "No missing ingredients."
    prompt = f"Suggest substitutions for these ingredients: {', '.join(missing_ingredients)}."
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=150, temperature=0.7
    )
    return response.choices[0].text.strip()

def generate_recipe(ingredients):
    """Generate a unique recipe using OpenAI."""
    prompt = f"Create a detailed recipe using these ingredients: {', '.join(ingredients)}."
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=300, temperature=0.9
    )
    return response.choices[0].text.strip()

def get_personalized_recipes(preferences, ingredients):
    """Get personalized recipe suggestions."""
    if not preferences:
        return None
    prompt = f"Recommend recipes based on these preferences: {preferences} and ingredients: {', '.join(ingredients)}."
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=150, temperature=0.7
    )
    return response.choices[0].text.strip()

if user_ingredients:
    # Process user ingredients
    user_ingredients = [ingredient.strip().lower() for ingredient in user_ingredients.split(",")]
    recipes = fetch_recipes(user_ingredients)

    # Filter recipes
    filtered_recipes = []
    for recipe in recipes:
        used_ingredients = [ing["name"] for ing in recipe["usedIngredients"]]
        missing_ingredients = [ing["name"] for ing in recipe["missedIngredients"]]
        total_ingredients = len(used_ingredients) + len(missing_ingredients)
        match_percentage = len(used_ingredients) / total_ingredients if total_ingredients > 0 else 0

        if match_percentage >= 0.3:
            filtered_recipes.append(
                {
                    "title": recipe["title"],
                    "url": f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-').lower()}-{recipe['id']}",
                    "image": recipe.get("image", ""),
                    "used_ingredients": used_ingredients,
                    "missing_ingredients": missing_ingredients,
                    "match_percentage": match_percentage,
                }
            )

    # Display recipes
    if filtered_recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in filtered_recipes:
            substitutes = suggest_substitutes(recipe["missing_ingredients"])
            recipe_html = f"""
            <div class="recipe-card">
                <img src="{recipe['image']}" alt="{recipe['title']}">
                <h3><a href="{recipe['url']}" target="_blank">{recipe['title']}</a></h3>
                <p>Matching Ingredients: {len(recipe['used_ingredients'])} / {len(recipe['used_ingredients']) + len(recipe['missing_ingredients'])} 
                <span class="match-percentage">({recipe['match_percentage']:.0%})</span></p>
                <p>Missing Ingredients: {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}</p>
                <p>Substitute Suggestions: {substitutes}</p>
            </div>
            """
            components.html(recipe_html, height=400)

    # AI-generated recipes
    st.subheader("📝 AI-Generated Recipe")
    generated_recipe = generate_recipe(user_ingredients)
    st.markdown(f"{generated_recipe}")

    # Personalized recipes
    if preferences:
        st.subheader("💡 Personalized Recipe Recommendations")
        personalized_recipes = get_personalized_recipes(preferences, user_ingredients)
        st.markdown(f"{personalized_recipes}")

else:
    st.info("Please enter some ingredients to get started!")

