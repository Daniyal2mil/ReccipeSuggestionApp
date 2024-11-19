import streamlit as st
import re
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Load the AI Model
@st.cache_resource
def load_model():
    model_name = "EleutherAI/gpt-neo-1.3B"  # Open-source GPT-Neo model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return generator

# Initialize the model
generator = load_model()

# Function to generate recipe suggestions
def generate_recipe_suggestions(ingredients):
    prompt = f"Suggest 3 recipes I can make using these ingredients: {', '.join(ingredients)}."
    try:
        response = generator(prompt, max_length=300, num_return_sequences=1)
        return response[0]["generated_text"]
    except Exception as e:
        st.error(f"Error generating recipes: {e}")
        return "No recipes available."

# Function to suggest substitutes
def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    try:
        response = generator(prompt, max_length=50, num_return_sequences=1)
        return response[0]["generated_text"]
    except Exception as e:
        st.error(f"Error generating substitute: {e}")
        return "No substitute found."

# Display the app title and description
st.title("🍲 AI-Powered Recipe Suggestion App (Open-Source)")
st.markdown("""<p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
    Get personalized recipe ideas, ingredient substitutions, and cooking tips with an open-source AI! 🤖</p>
""", unsafe_allow_html=True)

# Add input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Eggs, Tomatoes, Onions",
)

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
        tip_response = generator(tip_prompt, max_length=100, num_return_sequences=1)
        st.write(tip_response[0]["generated_text"])
    except Exception as e:
        st.error(f"Error fetching tip: {e}")
