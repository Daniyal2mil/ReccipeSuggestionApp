import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity

API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "41e111c99c94483697f95043f99064ec"  

def fetch_recipes(ingredients, number=50):
    params = {
        "ingredients": ",".join(ingredients),
        "apiKey": API_KEY,
        "number": number,
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

def preprocess_ingredients(ingredients):
    return [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in re.split(r",\s*|,\s*", ingredients)
        if ingredient.strip()
    ]

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
            "image": recipe.get("image", ""),  # Include image URL
            "label": label,
        })
    return pd.DataFrame(recipes)

def train_classification_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    model = LogisticRegression()
    model.fit(X, y)
    return model, vectorizer

def train_importance_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    regressor = RandomForestRegressor()
    regressor.fit(X.toarray(), y)
    return regressor

def recommend_recipes(user_ingredients, data, vectorizer, similarity_threshold=0.3, num_required_matches=1):
    user_input_vector = vectorizer.transform([" ".join(user_ingredients)])
    data["similarity"] = cosine_similarity(vectorizer.transform(data["ingredients"]), user_input_vector).flatten()
    
    recommendations = []
    for _, recipe in data.iterrows():
        used_ingredients_count = len([ing for ing in recipe["used_ingredients"] if ing in user_ingredients])
        if used_ingredients_count >= num_required_matches:
            recipe["matching_ingredients_count"] = used_ingredients_count
            recipe["total_ingredients_count"] = len(user_ingredients)
            recommendations.append(recipe)
    
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df["similarity_score"] = recommendations_df["matching_ingredients_count"].astype(str) + "/" + recommendations_df["total_ingredients_count"].astype(str)
    
    recommendations_df = recommendations_df.sort_values("matching_ingredients_count", ascending=False)
    
    return recommendations_df

st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("This app uses AI to suggest recipes based on ingredients!")

user_input = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
)

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    
    with st.spinner("Fetching recipes..."):
        api_response = fetch_recipes(user_ingredients)
    
    dataset = prepare_dataset(api_response, user_ingredients)
    
    with st.spinner("Training AI models..."):
        classification_model, vectorizer = train_classification_model(dataset)
        importance_model = train_importance_model(dataset)
    
    num_required_matches = st.slider(
        "Adjust Matching Ingredients (1-10):",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )
    
    recommendations = recommend_recipes(user_ingredients, dataset, vectorizer, similarity_threshold=0.3, num_required_matches=num_required_matches)
    
    if not recommendations.empty:
        st.subheader("🍴 AI-Recommended Recipes:")
        for _, recipe in recommendations.iterrows():
            st.image(recipe["image"], width=200, caption=recipe["title"])
            st.markdown(f"**[{recipe['title']}]({recipe['title']})**")
            st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
            st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
            st.markdown(f"**Matching Ingredients:** {recipe['matching_ingredients_count']} / {recipe['total_ingredients_count']}")
            st.markdown(f"**Similarity Score:** {recipe['similarity_score']}")
            st.markdown("---")
    else:
        st.error("No suitable recipes found. Try different ingredients!")







