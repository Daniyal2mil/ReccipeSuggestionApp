import streamlit as st
import requests
import re
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Replace with your actual API key

# Display the title and description of the app
st.title("🍲 Virtual Recipe Suggestion App")
st.markdown(
    """
    <p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
        Find recipes based on the ingredients you have on hand! 🍳
    </p>
    """,
    unsafe_allow_html=True,
)

# Add styling for all body text, cards, and recipe elements
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f8f4;
            color: #333;
        }
        .recipe-card {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-size: 1.1em;
        }
        .recipe-card img {
            width: 100%;
            height: auto;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .recipe-card a {
            text-decoration: none;
            color: #d97706;
            font-size: 1.2em;
            font-weight: bold;
        }
        .recipe-card a:hover {
            text-decoration: underline;
        }
        .recipe-card p {
            color: #555;
        }
        .header {
            text-align: center;
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 20px;
        }
        .ingredient-list {
            color: #3c763d;
            font-weight: bold;
        }
        .match-percentage {
            color: #5bc0de;
        }
        .missing-ingredients {
            color: #d9534f;
        }
        .input-box {
            width: 100%;
            padding: 10px;
            font-size: 1.1em;
            border-radius: 8px;
            border: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .input-box:focus {
            border-color: #3c763d;
            outline: none;
        }
    </style>
""", unsafe_allow_html=True)

# Define the cuisines mapping
cuisines = {
    'italian': 'italian',
    'mexican': 'mexican',
    'chinese': 'chinese',
    'indian': 'indian',
    'american': 'american',
    'french': 'french',
    'thai': 'thai',
    'japanese': 'japanese',
    'mediterranean': 'mediterranean',
    'greek': 'greek',
    'spanish': 'spanish',
    # Add more cuisines as needed
}

# Get user input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    key="ingredients_input",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
    help="Type ingredients you have at home to find recipes.",
    max_chars=200,
    label_visibility="visible",
)

# Prepare dataset from API response
def prepare_dataset(api_response, user_ingredients):
    recipes = []
    for recipe in api_response:
        used = [ing["name"].lower() for ing in recipe["usedIngredients"]]
        missed = [ing["name"].lower() for ing in recipe["missedIngredients"]]
        total_ingredients = used + missed
        label = 1 if len(used) / len(total_ingredients) >= 0.3 else 0
        # Add a valid cuisine label or 'unknown' if not mapped
        cuisine = cuisines.get(recipe["title"].lower(), "unknown")
        recipes.append({
            "title": recipe["title"],
            "ingredients": " ".join(total_ingredients),
            "used_ingredients": used,
            "missing_ingredients": missed,
            "image": recipe.get("image", ""),  # Include image URL
            "label": label,
            "cuisine": cuisine,
        })
    return pd.DataFrame(recipes)

# Train AI model for cuisine classification
def train_cuisine_model(data, cuisines):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["ingredients"])
    # Ensure that 'cuisine' is not empty and all labels are valid
    y = [cuisines.get(title.lower(), "unknown") for title in data["title"]]
    
    # Check if y contains valid cuisine labels
    if not all(label in cuisines.values() or label == "unknown" for label in y):
        st.error("Some cuisine labels are invalid or missing.")
        return None
    
    # Check that the lengths of X and y are the same
    if len(X) != len(y):
        st.error("Feature and label arrays have mismatched lengths.")
        return None
    
    # Fit model
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)
    return model

# Function to fetch recipes from the Spoonacular API
def fetch_recipes(ingredients):
    params = {
        "ingredients": ",".join(ingredients),
        "apiKey": API_KEY,
        "number": 50,  # Get a maximum of 50 recipes
        "ranking": 1,  # Rank based on ingredients match
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Spoonacular returns JSON data
    except requests.RequestException as e:
        if response.status_code == 401:
            st.error("Invalid API key. Please check your Spoonacular API key.")
        elif response.status_code == 402:
            st.error("API rate limit exceeded. Upgrade your Spoonacular plan.")
        else:
            st.error(f"Error fetching recipes: {e}")
        return []
    except ValueError:
        st.error("Invalid API response: Unable to parse JSON.")
        return []

if user_ingredients:
    # Convert user input to a cleaned list of ingredients
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in re.split(r",\s*|,\s*", user_ingredients)  # Split on commas and handle extra spaces
        if ingredient.strip()  # Ignore empty entries
    ]

    # Fetch recipes using Spoonacular API
    recipes = fetch_recipes(user_ingredients)

    # Prepare the dataset from the fetched recipes
    dataset = prepare_dataset(recipes, user_ingredients)

    # Train the AI model for cuisine classification
    cuisine_model = train_cuisine_model(dataset, cuisines)
    if cuisine_model is not None:
        st.write("Cuisine classification model trained successfully.")

    if recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in recipes:
            # Display each recipe card
            recipe_html = f"""
            <div class="recipe-card">
                <img src="{recipe['image']}" alt="{recipe['title']}">
                <h3><a href="https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-').lower()}-{recipe['id']}" target="_blank">{recipe['title']}</a></h3>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="ingredient-list">Matching Ingredients:</span> {len(recipe['used_ingredients'])} / {len(recipe['used_ingredients']) + len(recipe['missing_ingredients'])} 
                    <span class="match-percentage">({(len(recipe['used_ingredients']) / (len(recipe['used_ingredients']) + len(recipe['missing_ingredients']))):.0%})</span>
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="ingredient-list">Available Ingredients:</span> {', '.join(recipe['used_ingredients']) if recipe['used_ingredients'] else 'None'}
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="missing-ingredients">Missing Ingredients:</span> {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}
                </p>
            </div>
            """
            components.html(recipe_html, height=400)
    else:
        st.write("No matching recipes found. Try different ingredients.")

