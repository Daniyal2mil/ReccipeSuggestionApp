import streamlit as st
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your valid API key

# Fetch recipes from Spoonacular API
def fetch_recipes(ingredients, number=50, diet=None):
    params = {
        "ingredients": ",".join(ingredients),
        "apiKey": API_KEY,
        "number": number,
    }
    if diet:
        params["diet"] = diet
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
            "cuisine": "unknown",  # Placeholder for AI-predicted cuisine
        })
    return pd.DataFrame(recipes)

# Train AI model for recipe satisfaction rating
def train_rating_model(data):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = data["label"]
    regressor = RandomForestRegressor()
    regressor.fit(X.toarray(), y)
    return regressor

# Train AI model for cuisine classification
def train_cuisine_model(data, cuisines):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    y = [cuisines.get(title.lower(), "unknown") for title in data["title"]]
    model = LogisticRegression()
    model.fit(X, y)
    return model

# Cuisine Mappings
cuisines = {
    "spaghetti carbonara": "Italian",
    "chicken tikka masala": "Indian",
    "beef tacos": "Mexican",
    "pad thai": "Thai",
    "sushi": "Japanese",
    "chicken parmesan": "Italian",
    "ramen": "Japanese",
    "vegetable stir fry": "Chinese",
    "falafel": "Middle Eastern",
    "guacamole": "Mexican",
    "ceviche": "Peruvian",
    "moussaka": "Greek",
    "paella": "Spanish",
    # Add more mappings as needed
}

# Ingredient Substitutions
ingredient_substitutions = {
    "egg": "flaxseed meal (1 tbsp + 3 tbsp water) or chia seeds",
    "milk": "almond milk, oat milk, or coconut milk",
    "butter": "margarine, olive oil, or coconut oil",
    "chicken": "tofu, tempeh, or seitan",
    "sugar": "stevia, honey, or maple syrup",
    "flour": "almond flour, coconut flour, or oat flour",
    "cheese": "nutritional yeast, vegan cheese, or tofu",
    "cream": "coconut cream, cashew cream, or soy cream",
    "yogurt": "almond yogurt, coconut yogurt, or soy yogurt",
    "soy sauce": "tamari or coconut aminos",
    "vinegar": "lemon juice or lime juice",
    "salt": "sea salt, Himalayan salt, or tamari",
    "olive oil": "avocado oil, canola oil, or vegetable oil",
    "bacon": "tempeh bacon, coconut bacon, or mushrooms",
    "ground beef": "lentils, mushrooms, or plant-based ground meat",
    # Add more substitutions as needed
}

# Streamlit App
st.title("🍲 AI-Powered Recipe Suggestion App")
st.write("Find recipes tailored to your dietary needs and preferences!")

# User input
user_input = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
)

# Dietary preference
diet_option = st.selectbox(
    "Select your dietary preference:",
    ["None", "Gluten-Free", "Keto", "Vegetarian", "Vegan", "Dairy-Free", "Paleo"]
)
diet = None if diet_option == "None" else diet_option.lower()

if user_input:
    user_ingredients = preprocess_ingredients(user_input)
    
    # Fetch recipes from Spoonacular API
    with st.spinner("Fetching recipes..."):
        api_response = fetch_recipes(user_ingredients, diet=diet)
    
    # Prepare dataset from API response
    dataset = prepare_dataset(api_response, user_ingredients)
    
    # Train AI models dynamically
    with st.spinner("Training AI models..."):
        rating_model = train_rating_model(dataset)
        cuisine_model = train_cuisine_model(dataset, cuisines)
    
    # Recommend recipes
    st.subheader("🍴 AI-Recommended Recipes:")
    for _, recipe in dataset.iterrows():
        st.image(recipe["image"], width=200, caption=recipe["title"])
        st.markdown(f"**[{recipe['title']}]({recipe['title']})**")
        st.markdown(f"**Ingredients Used:** {', '.join(recipe['used_ingredients'])}")
        st.markdown(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients'])}")
        st.markdown("---")
    
    # Ingredient substitution suggestions
    st.subheader("🔄 Ingredient Substitutions:")
    for ingredient in user_ingredients:
        if ingredient in ingredient_substitutions:
            st.write(f"If you're out of {ingredient}, try using {ingredient_substitutions[ingredient]}!")
        else:
            st.write(f"No substitutions found for {ingredient}.")
