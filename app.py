import streamlit as st
import re
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = "meta-llama/Llama-2-7b-chat-hf"  # Update to your chosen Llama model

# Initialize Hugging Face Inference Client
try:
    hf_client = InferenceClient(model=HF_MODEL, token=HUGGINGFACE_API_KEY)
except Exception as e:
    st.error(f"Error initializing Hugging Face client: {e}")

# Function to test if the API key and model work
def test_api_key():
    test_prompt = "Hello, world!"
    try:
        response = hf_client.text_generation(prompt=test_prompt, max_new_tokens=10)
        if "generated_text" in response:
            st.success("Hugging Face API key and model are working correctly!")
            return True
        else:
            st.error("API key or model validation failed.")
            return False
    except Exception as e:
        st.error(f"API key validation error: {e}")
        return False

# Validate API key and model at startup
if not test_api_key():
    st.stop()  # Stop the app if validation fails

# Display the app title and description
st.title("🍲 AI-Powered Recipe Suggestion App with Llama 2")
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
        response = hf_client.text_generation(prompt=prompt, max_new_tokens=300)
        return response["generated_text"]
    except Exception as e:
        st.error(f"Error generating recipes: {e}")
        return "No recipes available."

def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    try:
        response = hf_client.text_generation(prompt=prompt, max_new_tokens=50)
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
        tip_response = hf_client.text_generation(prompt=tip_prompt, max_new_tokens=100)
        st.write(tip_response["generated_text"])
    except Exception as e:
        st.error(f"Error fetching tip: {e}")
