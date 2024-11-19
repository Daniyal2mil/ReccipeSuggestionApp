import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
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
            "dietary_info": recipe.get("dietaryPreferences", []),  # Assuming dietary info is available
        })
    return pd.DataFrame(recipes)

# Train AI model for recipe classification (match with user ingredients)
def train_classification_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    model = LogisticRegression()
    model.fit(X, y)
    return model, vectorizer

# Train AI model for dietary preference classification
def train_dietary_model(data):
    dietary_labels = {"vegan": 0, "gluten-free": 1, "keto": 2, "vegetarian": 3}  # Example dietary categories
    data["dietary_labels"] = data["dietary_info"].apply(lambda x: [dietary_labels[cat] for cat in x if cat in dietary_labels])
    data = data.explode("dietary_labels").dropna(subset=["dietary_labels"])

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["dietary_labels"]
    model = RandomForestClassifier()
    model.fit(X, y)
    return model, vectorizer

# Recommend recipes based on similarity
def recommend_recipes(user_ingredients, data, model, vectorizer):
    user_input_vector = vectorizer.transform([" ".join(user_ingredients)])
    data["similarity"] = cosine_similarity(vectorizer.transform(data["ingredients"]), user_input_vector).flatten()
    recommendations = data.sort_values("similarity", ascending=False)
    return recommendations

# Streamlit App
st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("This app uses AI to suggest recipes based on ingredients and dietary preferences!")

# User input
user_input = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
)

user_dietary_preference = st.selectbox(
    "Select your dietary preference:",
    options=["None", "Vegan", "Gluten-Free", "Keto", "Vegetarian"],
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
    
    # Recommend recipes based on similarity (no threshold slider)
    recommendations = recommend_recipes(user_ingredients, dataset, classification_model, vectorizer)
    
    # Filter recommendations by dietary preference using AI model
    if user_dietary_preference != "None":
        dietary_labels = {"Vegan": 0, "Gluten-Free": 1, "Keto": 2, "Vegetarian": 3}
        dietary_preference_label = dietary_labels.get(user_dietary_preference, None)
        if dietary_preference_label is not None:
            recommendations["dietary_match"] = recommendations["dietary_info"].apply(
                lambda x: dietary_preference_label in x
            )
            recommendations = recommendations[recommendations["dietary_match"]]
    
    # Mark the best recommended recipe based on AI score
    if not recommendations.empty:
        best_recipe = recommendations.iloc[0]
        st.subheader("🍴 Best AI-Recommended Recipe:")
        st.image(best_recipe["image"], width=200, caption=best_recipe["title"])
        st.markdown(f"**[{best_recipe['title']}]({best_recipe['title']})**")
        st.markdown(f"**Ingredients Used:** {', '.join(best_recipe['used_ingredients'])}")
        st.markdown(f"**Missing Ingredients:** {', '.join(best_recipe['missing_ingredients'])}")
        st.markdown(f"**Similarity Score:** {best_recipe['similarity']:.2f}")
        st.markdown(f"**Dietary Info:** {', '.join(best_recipe['dietary_info'])}")
    else:
        st.error("No suitable recipes found. Try different ingredients or dietary preferences!")

    # Show all other recommended recipes
    st.subheader("🍴 Other AI-Recommended Recipes:")
    for _, recipe in recommendations.iterrows():
        st.image(recipe["image"], width=200, caption=recipe["title"])
        st.markdown(f"**[{recipe['title']}]({recipe['title']})**")
        st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
        st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
        st.markdown(f"**Similarity Score:** {recipe['similarity']:.2f}")
        st.markdown(f"**Dietary Info:** {', '.join(recipe['dietary_info'])}")
        st.markdown("---")
