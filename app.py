import re
import streamlit as st
import requests
from transformers import pipeline
from sklearn.externals import joblib

# Spoonacular API Setup
SPOONACULAR_API_KEY = "25d917fef9554ad3b05f732cd181a39f"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="distilgpt2", tokenizer="distilgpt2")

gpt2 = load_gpt2_model()

# Load a prebuilt model (assuming a model exists)
model = joblib.load('text_classifier_model.pkl')  # Replace with actual model file path

# Function to get recipes from Spoonacular
@st.cache
def fetch_recipes(ingredients, diet_preference):
    params = {
        "ingredients": ingredients,
        "number": 3,  # Limit the number of recipes to 3
        "ranking": 1,
        "diet": diet_preference,  # Include the dietary preference
        "apiKey": SPOONACULAR_API_KEY,
    }
    response = requests.get(SPOONACULAR_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching recipes from Spoonacular API")
        return []

# Clean and format GPT-2 output
def clean_and_format_gpt2_output(raw_text):
    # Extract and structure sections using regex
    title_match = re.search(r"(Recipe Name:|Title:)(.*)", raw_text, re.IGNORECASE)
    title = title_match.group(2).strip() if title_match else "Untitled Recipe"
    
    ingredients_match = re.search(r"(Ingredients:)(.*?)(Steps:|Instructions:)", raw_text, re.IGNORECASE | re.DOTALL)
    ingredients = ingredients_match.group(2).strip() if ingredients_match else "No ingredients listed."
    
    steps_match = re.search(r"(Steps:|Instructions:)(.*)", raw_text, re.IGNORECASE | re.DOTALL)
    steps = steps_match.group(2).strip() if steps_match else "No steps provided."
    
    # Format sections
    formatted = f"### {title}\n\n**Ingredients:**\n{ingredients}\n\n**Instructions:**\n{steps}"
    return formatted

# Function to predict if search is ingredients-based or normal
def predict_search_type(query):
    return model.predict([query])[0]

# Streamlit App
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients or search by a normal query to get recipe suggestions, enhanced by AI!")

# Input for ingredients or normal search
query = st.text_area("Enter your query (ingredients or search term):", placeholder="e.g., tomato, cheese, basil or Pasta dishes")

# Dropdown for dietary preferences
diet_choices = ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Paleo', 'Keto']
diet_preference = st.selectbox("Select dietary preference:", diet_choices)

if st.button("Generate Recipes"):
    if query.strip():
        # Predict the search type (ingredients or normal search)
        search_type = predict_search_type(query)

        with st.spinner("Fetching recipes..."):
            if search_type == "ingredients":
                # Fetch recipes based on ingredients
                recipes = fetch_recipes(query, diet_preference if diet_preference != 'None' else '')
                
                if recipes:
                    st.subheader("Recipes based on Ingredients:")
                    for recipe in recipes:
                        # Check available and missing ingredients
                        available_ingredients = [ingredient for ingredient in recipe['ingredients'] if ingredient in query]
                        missing_ingredients = list(set(recipe['ingredients']) - set(available_ingredients))

                        st.markdown(f"### {recipe['title']}")
                        st.image(recipe.get("image", ""), width=300)

                        st.write(f"**Available ingredients**: {', '.join(available_ingredients)}")
                        st.write(f"**Missing ingredients**: {', '.join(missing_ingredients)}")

                        # Enhance with GPT-2
                        prompt = f"Generate a well-structured recipe based on {recipe['title']} and the ingredients: {query}. Include a title, ingredients, and clear steps. Ensure the recipe fits a {diet_preference} diet."
                        raw_ai_recipe = gpt2(prompt, max_length=150, num_return_sequences=1)[0]["generated_text"]

                        # Clean and format output
                        formatted_recipe = clean_and_format_gpt2_output(raw_ai_recipe)
                        st.markdown("**AI-Enhanced Recipe**")
                        st.markdown(formatted_recipe, unsafe_allow_html=True)
                else:
                    st.error("No recipes found!")
            else:
                # Fetch normal recipes
                recipes = fetch_recipes(query, diet_preference if diet_preference != 'None' else '')
                
                if recipes:
                    st.subheader("Normal Recipe Search Results:")
                    for recipe in recipes:
                        st.markdown(f"### {recipe['title']}")
                        st.image(recipe.get("image", ""), width=300)

                        # Enhance with GPT-2
                        prompt = f"Generate a well-structured recipe based on {recipe['title']} and the ingredients: {query}. Include a title, ingredients, and clear steps. Ensure the recipe fits a {diet_preference} diet."
                        raw_ai_recipe = gpt2(prompt, max_length=150, num_return_sequences=1)[0]["generated_text"]

                        # Clean and format output
                        formatted_recipe = clean_and_format_gpt2_output(raw_ai_recipe)
                        st.markdown("**AI-Enhanced Recipe**")
                        st.markdown(formatted_recipe, unsafe_allow_html=True)
        else:
            st.error("Please enter a valid query!")





