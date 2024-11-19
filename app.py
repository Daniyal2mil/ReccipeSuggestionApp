import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your valid API key

# Fetch recipes from Spoonacular API
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
            "image": recipe.get("image", ""),  # Include image URL
            "label": label,
        })
    return pd.DataFrame(recipes)

# Train AI model for recipe classification
def train_classification_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    model = LogisticRegression()
    model.fit(X, y)
    return model, vectorizer

# Train AI model for ingredient importance
def train_importance_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    regressor = RandomForestRegressor()
    regressor.fit(X.toarray(), y)
    return regressor

# Recommend recipes
def recommend_recipes(user_ingredients, data, model, vectorizer, similarity_threshold=0.3):
    user_input_vector = vectorizer.transform([" ".join(user_ingredients)])
    data["similarity"] = cosine_similarity(vectorizer.transform(data["ingredients"]), user_input_vector).flatten()
    recommendations = data[data["similarity"] >= similarity_threshold].sort_values("similarity", ascending=False)
    return recommendations

# Cluster recipes using K-Means
def cluster_recipes(data, n_clusters=3):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    data["cluster"] = kmeans.fit_predict(X)
    return data, kmeans

# Streamlit App
st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("This app uses AI to suggest recipes and discover new insights!")

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
    
    # Train AI models dynamically
    with st.spinner("Training AI models..."):
        classification_model, vectorizer = train_classification_model(dataset)
        importance_model = train_importance_model(dataset)
        clustered_data, kmeans_model = cluster_recipes(dataset)
    
    # Adjustable similarity threshold
    similarity_threshold = st.slider("Adjust Matching Threshold:", 0.1, 1.0, 0.3, 0.1)
    
    # Recommend recipes
    recommendations = recommend_recipes(user_ingredients, dataset, classification_model, vectorizer, similarity_threshold)
    
    if not recommendations.empty:
        st.subheader("🍴 AI-Recommended Recipes:")
        for _, recipe in recommendations.iterrows():
            st.image(recipe["image"], width=200, caption=recipe["title"])
            st.markdown(f"**[{recipe['title']}]({recipe['title']})**")
            st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
            st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
            st.markdown(f"**Similarity Score:** {recipe['similarity']:.2f}")
            st.markdown("---")
    else:
        st.error("No suitable recipes found. Try different ingredients!")
    
    # Show clusters
    st.subheader("🍴 Recipe Clusters:")
    st.write(clustered_data.groupby("cluster")["title"].apply(list))
