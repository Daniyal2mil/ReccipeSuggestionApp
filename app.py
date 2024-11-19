import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
import numpy as np

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
            "used_count": len(used),
            "missing_count": len(missed),
        })
    return pd.DataFrame(recipes)

# Train an AI model for recipe scoring
def train_recipe_model(data):
    vectorizer = TfidfVectorizer()
    ingredient_vectors = vectorizer.fit_transform(data["ingredients"].apply(lambda x: " ".join(x)))
    scores = data["used_count"] - data["missing_count"]  # Simplified scoring: more used, fewer missing
    model = RandomForestRegressor()
    model.fit(ingredient_vectors.toarray(), scores)
    return model, vectorizer

# Recommend recipes with AI scoring
def recommend_recipes(user_ingredients, data, model, vectorizer, weight=0.5):
    user_vector = vectorizer.transform([" ".join(user_ingredients)]).toarray()
    data_vectors = vectorizer.transform(data["ingredients"].apply(lambda x: " ".join(x))).toarray()
    
    # Calculate similarity and predict scores
    similarities = cosine_similarity(data_vectors, user_vector).flatten()
    predictions = model.predict(data_vectors)
    
    # Combine similarity and predictions for final score
    data["ai_score"] = weight * similarities + (1 - weight) * predictions
    return data.sort_values("ai_score", ascending=False)

# Streamlit App
st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("Find recipes using AI to match your available ingredients with suggestions tailored to your needs!")

# User input
user_input = st.text_input(
    "Enter ingredients you have (comma-separated):",
    placeholder="e.g., chicken, rice, onion",
    help="List the ingredients you have, and AI will find the best recipes."
)

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    st.write(f"**Your Ingredients:** {', '.join(user_ingredients)}")

    # Fetch recipes
    with st.spinner("Fetching recipes..."):
        try:
            api_response = fetch_recipes(user_ingredients)
            dataset = prepare_dataset(api_response)

            # Train AI model
            with st.spinner("Training AI model..."):
                model, vectorizer = train_recipe_model(dataset)

            # Adjust AI scoring weight
            weight = st.slider(
                "Adjust AI scoring weight (0: ingredient match, 1: AI prediction):",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
            )

            # Recommend recipes
            recommendations = recommend_recipes(user_ingredients, dataset, model, vectorizer, weight)

            # Display recommendations
            if not recommendations.empty:
                st.subheader("🍴 Recommended Recipes")
                for _, recipe in recommendations.iterrows():
                    st.image(recipe["image"], width=200)
                    st.markdown(f"### [{recipe['title']}]({recipe['source_url']})")
                    st.markdown(f"- **Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
                    st.markdown(f"- **Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
                    st.markdown(f"- **AI Score:** {recipe['ai_score']:.2f}")
                    st.markdown("---")
            else:
                st.error("No recipes found. Try different ingredients.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")

