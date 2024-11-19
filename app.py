import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
def prepare_dataset(api_response, user_ingredients):
    recipes = []
    for recipe in api_response:
        used = [ing["name"].lower() for ing in recipe["usedIngredients"]]
        missed = [ing["name"].lower() for ing in recipe["missedIngredients"]]
        recipes.append({
            "title": recipe["title"],
            "ingredients": used + missed,
            "used_count": len(used),
            "missing_count": len(missed),
            "total_ingredients": len(used) + len(missed),
            "image": recipe.get("image", ""),
            "source_url": recipe.get("sourceUrl", ""),
        })
    return pd.DataFrame(recipes)

# Recommend recipes
def recommend_recipes(user_ingredients, data):
    data["match_score"] = data["used_count"] / data["total_ingredients"]
    return data.sort_values("match_score", ascending=False)

# Streamlit App
st.title("🍲 Recipe Suggestion App")
st.write("Find delicious recipes based on the ingredients you have!")

# User input
user_input = st.text_input(
    "Enter ingredients (comma-separated):",
    placeholder="e.g., chicken, rice, onion",
    help="List ingredients you have on hand to get recipe suggestions."
)

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    st.write(f"**Your Ingredients:** {', '.join(user_ingredients)}")

    # Fetch recipes
    with st.spinner("Fetching recipes..."):
        try:
            api_response = fetch_recipes(user_ingredients)
            dataset = prepare_dataset(api_response, user_ingredients)

            # Recommend recipes
            recommendations = recommend_recipes(user_ingredients, dataset)

            if not recommendations.empty:
                st.subheader("🍴 Recommended Recipes")
                for _, recipe in recommendations.iterrows():
                    st.image(recipe["image"], width=200)
                    st.markdown(f"### [{recipe['title']}]({recipe['source_url']})")
                    st.markdown(f"- **Ingredients Used:** {recipe['used_count']}")
                    st.markdown(f"- **Missing Ingredients:** {recipe['missing_count']}")
                    st.markdown(f"---")
            else:
                st.error("No recipes found. Try different ingredients.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")
