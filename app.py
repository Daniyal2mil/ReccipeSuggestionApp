import streamlit as st
import re
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = "gpt2"  # Replace with your preferred model

# Initialize Hugging Face Inference Client
hf_client = InferenceClient(model=HF_MODEL, token=HUGGINGFACE_API_KEY)

# Display the app title and description
st.title("🍲 AI-Powered Recipe Suggestion App")
st.markdown("""
    <p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
        Get personalized recipe ideas, ingredient substitutions, and cooking tips with AI! 🤖
    </p>
    """, unsafe_allow_html=True)

# Add input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Eggs, Tomatoes, Onions",
)

# AI Functionality
def generate_recipe_suggestions(ingredients):
    prompt = f"Suggest 3 recipes I can make using these ingredients: {', '.join(ingredients)}."
    try:
        response = hf_client.generate(prompt=prompt, max_length=200)
        return response["generated_text"]
    except Exception as e:
        st.error(f"Error generating recipes: {e}")
        return "No recipes available."

def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    try:
        response = hf_client.generate(prompt=prompt, max_length=50)
        return response["generated_text"]
    except Exception as e:
        st.error(f"Error generating substitute: {e}")
        return "No substitute found."

# Process user input
if user_ingredients:
    ingredients = [re.sub(r"\s+", " ", ing.strip().lower()) for ing in user_ingredients.split(",") if ing.strip()]
    
    # Get AI recipe suggestions
    st.subheader("🍴 AI-Powered Recipe Suggestions:")
    recipes = generate_recipe_suggestions(ingredients)
    st.write(recipes)
    
    # Get AI ingredient substitutions
    st.subheader("🧑‍🍳 Ingredient Substitutions:")
    for ingredient in ingredients:
        substitute = suggest_substitute(ingredient)
        st.markdown(f"**Substitute for {ingredient}:** {substitute}")

# Add additional AI functionalities
st.subheader("✨ Cooking Tips and Tricks:")
if st.button("Get a Cooking Tip"):
    tip_prompt = "Give me a useful cooking tip for beginners."
    try:
        tip_response = hf_client.generate(prompt=tip_prompt, max_length=100)
        st.write(tip_response["generated_text"])
    except Exception as e:
        st.error(f"Error fetching tip: {e}")
