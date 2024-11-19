import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier

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
        # Removed the 30% label rule
        recipes.append({
            "title": recipe["title"],
            "ingredients": " ".join(total_ingredients),
            "used_ingredients": used,
            "missing_ingredients": missed,
            "image": recipe.get("image", ""),  # Include image URL
            "nutrition": recipe.get("nutrition", {}),  # Nutritional data (if available)
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

# Train AI model for dietary preference classification
def train_dietary_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    
    # Create labels for dietary preferences (you can use more complex rules or manual labeling)
    def dietary_label(row):
        if 'gluten' in row['ingredients'] and 'milk' not in row['ingredients']:
            return 'gluten_free'
        elif 'milk' in row['ingredients']:
            return 'not_gluten_free'
        else:
            return 'other'

    data['dietary_preference'] = data.apply(dietary_label, axis=1)
    y = data['dietary_preference']
    
    model = RandomForestClassifier()
    model.fit(X, y)
    return model, vectorizer

# Recommend recipes
def recommend_recipes(user_ingredients, data, model, vectorizer):
    user_input_vector = vectorizer.transform([" ".join(user_ingredients)])
    data["similarity"] = cosine_similarity(vectorizer.transform(data["ingredients"]), user_input_vector).flatten()
    recommendations = data.sort_values("similarity", ascending=False)
    return recommendations

# AI-powered dietary preference filter
def filter_by_dietary_preference(data, dietary_preference, model, vectorizer):
    # Predict the dietary preference for each recipe using the trained model
    data['predicted_dietary'] = model.predict(vectorizer.transform(data['ingredients']))
    
    # Filter based on user selected dietary preference
    filtered_data = data[data['predicted_dietary'] == dietary_preference]
    return filtered_data

# Streamlit App
st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("This app uses AI to suggest recipes based on ingredients and dietary preferences!")

# User input
user_input = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
)

dietary_preference = st.selectbox(
    "Choose your dietary preference:",
    options=["None", "Gluten-Free", "Keto", "Vegetarian", "Vegan"]
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
        dietary_model, dietary_vectorizer = train_dietary_model(dataset)
    
    # Recommend recipes based on user input (no threshold slider)
    recommendations = recommend_recipes(user_ingredients, dataset, classification_model, vectorizer)
    
    # Filter recipes by dietary preference (if selected)
    if dietary_preference != "None":
        recommendations = filter_by_dietary_preference(recommendations, dietary_preference.lower().replace(" ", "_"), dietary_model, dietary_vectorizer)
    
    if not recommendations.empty:
        st.subheader("🍴 AI-Recommended Recipes:")
        
        # Mark the best recipe based on similarity
        best_recipe = recommendations.iloc[0]
        st.markdown("### Best AI-Recommended Recipe")
        st.image(best_recipe["image"], width=200, caption=best_recipe["title"])
        st.markdown(f"**[{best_recipe['title']}]**")
        st.markdown(f"**Ingredients Used:** {', '.join(best_recipe['used_ingredients'])}")
        st.markdown(f"**Missing Ingredients:** {', '.join(best_recipe['missing_ingredients'])}")
        st.markdown(f"**Similarity Score:** {best_recipe['similarity']:.2f}")
        st.markdown(f"**Nutrition Info (if available):** {best_recipe['nutrition']}")
        st.markdown("---")
        
        # Show other recipes
        for _, recipe in recommendations.iloc[1:].iterrows():
            st.image(recipe["image"], width=200, caption=recipe["title"])
            st.markdown(f"**[{recipe['title']}]**")
            st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
            st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
            st.markdown(f"**Similarity Score:** {recipe['similarity']:.2f}")
            st.markdown(f"**Nutrition Info (if available):** {recipe['nutrition']}")
            st.markdown("---")
    else:
        st.error("No suitable recipes found. Try different ingredients or dietary preferences!")










