import streamlit as st
import requests
import re
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
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
            "ingredients": " ".join(used + missed),
            "used_ingredients": used,
            "missing_ingredients": missed,
            "image": recipe.get("image", ""),
            "source_url": recipe.get("sourceUrl", ""),
            "vegan": recipe.get("vegan", False),
            "glutenFree": recipe.get("glutenFree", False),
            "keto": recipe.get("keto", False),
        })
    return pd.DataFrame(recipes)

# Train a dietary classification model
def train_dietary_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data[["vegan", "glutenFree", "keto"]].astype(int)

    model = RandomForestClassifier()
    model.fit(X, y)

    # Save model and vectorizer for later use
    with open("dietary_model.pkl", "wb") as f:
        pickle.dump((model, vectorizer), f)

    return model, vectorizer

# Load the trained model and vectorizer
def load_dietary_model():
    with open("dietary_model.pkl", "rb") as f:
        return pickle.load(f)

# Predict recipes based on dietary preferences
def predict_recipes(user_ingredients, model, vectorizer, dataset, preferences):
    user_vector = vectorizer.transform([" ".join(user_ingredients)])
    predictions = model.predict(user_vector)
    
    # Map predictions back to preferences
    preference_map = {0: "vegan", 1: "glutenFree", 2: "keto"}
    preference_results = {preference_map[i]: bool(pred) for i, pred in enumerate(predictions.flatten())}

    # Filter dataset based on predictions and user preferences
    filtered_data = dataset
    for pref in preferences:
        if preference_results.get(pref, False):
            filtered_data = filtered_data[filtered_data[pref] == True]

    return filtered_data

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
    options=["vegan", "glutenFree", "keto"],
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

            # Check if model exists, train if not
            try:
                model, vectorizer = load_dietary_model()
            except FileNotFoundError:
                st.warning("Training AI model for the first time...")
                model, vectorizer = train_dietary_model(dataset)

            # Predict recipes based on user input and preferences
            filtered_data = predict_recipes(user_ingredients, model, vectorizer, dataset, dietary_preferences)

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
