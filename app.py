import re
import streamlit as st
import requests
from transformers import pipeline

# Spoonacular API Setup
SPOONACULAR_API_KEY = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="gpt2", tokenizer="gpt2")

gpt2 = load_gpt2_model()

# Function to get recipes from Spoonacular
def fetch_recipes(ingredients, diet_preference):
    params = {
        "ingredients": ingredients,
        "number": 3,
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

# Streamlit App
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients and select a dietary preference to get recipe suggestions, enhanced by AI!")

# Input for ingredients
ingredients = st.text_area("Enter ingredients (comma-separated):", placeholder="e.g., tomato, cheese, basil")

# Dropdown for dietary preferences
diet_choices = ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Paleo', 'Keto']
diet_preference = st.selectbox("Select dietary preference:", diet_choices)

if st.button("Generate Recipes"):
    if ingredients.strip():
        if diet_preference == 'None':
            diet_preference = ''  # No specific dietary preference

        with st.spinner("Fetching recipes..."):
            recipes = fetch_recipes(ingredients, diet_preference)
        
        if recipes:
            st.subheader("Recipes from Spoonacular:")
            for recipe in recipes:
                st.markdown(f"### {recipe['title']}")
                st.image(recipe.get("image", ""), width=300)
                
                # Enhance with GPT-2
                prompt = f"Generate a well-structured recipe based on {recipe['title']} and the ingredients: {ingredients}. Include a title, ingredients, and clear steps. Ensure the recipe fits a {diet_preference} diet."
                raw_ai_recipe = gpt2(prompt, max_length=300, num_return_sequences=1)[0]["generated_text"]
                
                # Clean and format output
                formatted_recipe = clean_and_format_gpt2_output(raw_ai_recipe)
                
                st.markdown("**AI-Enhanced Recipe**")
                st.markdown(formatted_recipe, unsafe_allow_html=True)
        else:
            st.error("No recipes found!")
    else:
        st.error("Please enter some ingredients!")




