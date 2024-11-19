import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your valid API key

# Function to fetch recipes from Spoonacular API
def fetch_recipes(ingredients, number=50):
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
        total_ingredients = used + missed
        label = 1 if len(used) / len(total_ingredients) >= 0.3 else 0
        recipes.append({
            "title": recipe["title"],
            "ingredients": " ".join(total_ingredients),
            "used_ingredients": used,
            "missing_ingredients": missed,
            "label": label,
        })
    return pd.DataFrame(recipes)

# Train AI model
def train_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    model = LogisticRegression()
    model.fit(X, y)
    return model, vectorizer

# Recommend recipes
def recommend_recipes(user_ingredients, data, model, vectorizer):
    user_input_vector = vectorizer.transform([" ".join(user_ingredients)])
    data["similarity"] = cosine_similarity(vectorizer.transform(data["ingredients"]), user_input_vector).flatten()
    recommendations = data.sort_values("similarity", ascending=False).head(5)  # Top 5 recommendations
    return recommendations

# Streamlit App
st.title("🍲 Virtual Recipe Suggestion App with AI")
st.write("This app uses AI to suggest recipes based on your ingredients!")

# User input
user_input = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
)

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    
    # Fetch recipes from Spoonacular API
    with st.spinner("Fetching recipes..."):
        api_response = fetch_recipes(user_ingredients)
    
    # Prepare dataset from API response
    dataset = prepare_dataset(api_response, user_ingredients)
    
    # Train AI model dynamically
    with st.spinner("Training AI model..."):
        model, vectorizer = train_model(dataset)
    
    # Recommend recipes
    recommendations = recommend_recipes(user_ingredients, dataset, model, vectorizer)
    
    if not recommendations.empty:
        st.subheader("🍴 AI-Recommended Recipes:")
        for _, recipe in recommendations.iterrows():
            st.markdown(f"**[{recipe['title']}]({recipe['title']})**")
            st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
            st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
            st.markdown(f"**Similarity Score:** {recipe['similarity']:.2f}")
            st.markdown("---")
    else:
        st.error("No suitable recipes found. Try different ingredients!")

