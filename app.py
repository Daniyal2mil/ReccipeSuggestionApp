import streamlit as st
import re
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

# Function to test if the API key works
def test_api_key():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Say 'Hello, world!'"}]
        )
        if response:
            st.success("OpenAI API key is working correctly!")
            return True
        else:
            st.error("API key validation failed.")
            return False
    except Exception as e:
        st.error(f"API key validation error: {e}")
        return False

# Validate API key at startup
if not test_api_key():
    st.stop()  # Stop the app if validation fails

# Display the app title and description
st.title("🍲 AI-Powered Recipe Suggestion App with GPT")
st.markdown("""<p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
    Get personalized recipe ideas, ingredient substitutions, and cooking tips with AI! 🤖</p>
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating recipes: {e}")
        return "No recipes available."

def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response['choices'][0]['message']['content']
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
        tip_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": tip_prompt}],
            max_tokens=100
        )
        st.write(tip_response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"Error fetching tip: {e}")
