import streamlit as st
import requests
from transformers import pipeline

# Spoonacular API Setup
SPOONACULAR_API_KEY = "25d917fef9554ad3b05f732cd181a39f"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="gpt2", tokenizer="gpt2")

gpt2 = load_gpt2_model()

# Function to get recipes from Spoonacular
def fetch_recipes(ingredients):
    params = {
        "ingredients": ingredients,
        "number": 3,
        "ranking": 1,
        "apiKey": SPOONACULAR_API_KEY,
    }
    response = requests.get(SPOONACULAR_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching recipes from Spoonacular API")
        return []

# Streamlit App
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients to get recipe suggestions, enhanced by AI!")

# Input for ingredients
ingredients = st.text_area("Enter ingredients (comma-separated):", placeholder="e.g., tomato, cheese, basil")

if st.button("Generate Recipes"):
    if ingredients.strip():
        with st.spinner("Fetching recipes..."):
            recipes = fetch_recipes(ingredients)
        
        if recipes:
            st.subheader("Recipes from Spoonacular:")
            for recipe in recipes:
                st.markdown(f"### {recipe['title']}")
                st.image(recipe.get("image", ""), width=300)
                
                # Enhance with GPT-2
                prompt = f"Enhance this recipe: {recipe['title']} with ingredients {ingredients}. Provide a story and tips."
                ai_enhanced_recipe = gpt2(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
                
                st.write("**AI-Enhanced Recipe**")
                st.write(ai_enhanced_recipe)
        else:
            st.error("No recipes found!")
    else:
        st.error("Please enter some ingredients!")


