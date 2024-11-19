import streamlit as st
import requests
import re
import pandas as pd

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your valid API key

# Fetch recipes from Spoonacular API
def fetch_recipes(ingredients, number=20):
    params = {
        "ingredients": ",".join(ingredients),
        "apiKey": API_KEY,
        "number": number,
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

# Preprocess ingredients
def preprocess_ingredients(ingredients):
    return [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in re.split(r",\s*|,\s*", ingredients)
        if ingredient.strip()
    ]

# Prepare dataset from API response
def prepare_dataset(api_response):
    recipes = []
    for recipe in api_response:
        used = [ing["name"].lower() for ing in recipe["usedIngredients"]]
        missed = [ing["name"].lower() for ing in recipe["missedIngredients"]]
        recipes.append({
            "title": recipe["title"],
            "ingredients": used + missed,
            "used_ingredients": used,
            "missing_ingredients": missed,
            "image": recipe.get("image", ""),
            "source_url": recipe.get("sourceUrl", ""),
        })
    return pd.DataFrame(recipes)

# Dietary rules
DIETARY_RULES = {
    "vegan": lambda ingredients: not any(
        item in ingredients
        for item in ["meat", "chicken", "fish", "egg", "milk", "cheese", "butter", "honey"]
    ),
    "vegetarian": lambda ingredients: not any(
        item in ingredients for item in ["meat", "chicken", "fish"]
    ),
    "keto": lambda ingredients: not any(
        item in ingredients
        for item in ["sugar", "bread", "pasta", "rice", "potato", "flour"]
    ),
    "glutenFree": lambda ingredients: not any(
        item in ingredients for item in ["wheat", "barley", "rye", "flour", "bread", "pasta"]
    ),
}

# Classify recipes based on dietary rules
def classify_recipes(dataset, preferences):
    filtered_recipes = dataset.copy()

    for pref in preferences:
        rule = DIETARY_RULES.get(pref)
        if rule:
            filtered_recipes = filtered_recipes[
                filtered_recipes["ingredients"].apply(lambda x: rule(x))
            ]

    return filtered_recipes

# Streamlit App
st.title("🍲 AI-Powered Recipe Finder with Dietary Preferences")
st.write("Find recipes using AI that match your ingredients and dietary needs!")

# User input
user_input = st.text_input(
    "Enter ingredients you have (comma-separated):",
    placeholder="e.g., chicken, rice, onion",
    help="List the ingredients you have, and AI will find recipes tailored to your preferences."
)

# Dietary preference selection
dietary_preferences = st.multiselect(
    "Select your dietary preferences:",
    options=["vegan", "vegetarian", "keto", "glutenFree"],
    help="Filter recipes to match your dietary needs."
)

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    st.write(f"**Your Ingredients:** {', '.join(user_ingredients)}")

    # Fetch recipes
    with st.spinner("Fetching recipes..."):
        try:
            api_response = fetch_recipes(user_ingredients)
            dataset = prepare_dataset(api_response)

            # Filter recipes based on dietary preferences
            filtered_data = classify_recipes(dataset, dietary_preferences)

            # Display filtered recipes
            if not filtered_data.empty:
                st.subheader("🍴 Filtered Recipes")
                for _, recipe in filtered_data.iterrows():
                    st.image(recipe["image"], width=200)
                    st.markdown(f"### [{recipe['title']}]({recipe['source_url']})")
                    st.markdown(f"- **Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
                    st.markdown(f"- **Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
                    st.markdown("---")
            else:
                st.error("No recipes found matching your dietary preferences. Try different filters.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")
