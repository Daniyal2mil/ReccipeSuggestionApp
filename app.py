import streamlit as st
import re
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Load the AI Model
@st.cache_resource
def load_model():
    model_name = "EleutherAI/gpt-neo-1.3B"  # Open-source GPT-Neo model
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models")
    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir="./models")
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return generator

# Initialize the model
generator = load_model()

# Function to generate recipe suggestions
def generate_recipe_suggestions(ingredients):
    prompt = f"Suggest 3 recipes I can make using these ingredients: {', '.join(ingredients)}."
    response = generator(prompt, max_length=250, num_return_sequences=1, truncation=True)
    return response[0]["generated_text"]

# Function to suggest substitutes
def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    response = generator(prompt, max_length=50, num_return_sequences=1, truncation=True)
    return response[0]["generated_text"]

# Function to generate cooking tips
def get_cooking_tip():
    prompt = "Give me a useful cooking tip for beginners."
    response = generator(prompt, max_length=100, num_return_sequences=1, truncation=True)
    return response[0]["generated_text"]

# Streamlit App Interface
st.title("🍲 AI-Powered Recipe Generator (Offline)")
st.markdown("""<p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
    Get personalized recipes, ingredient substitutions, and cooking tips—all offline and free! 🤖</p>
""", unsafe_allow_html=True)

# Add input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    placeholder="e.g., Eggs, Tomatoes, Onions",
)

if user_ingredients:
    # Process input ingredients
    ingredients = [re.sub(r"\s+", " ", ing.strip().lower()) for ing in user_ingredients.split(",") if ing.strip()]

    # Generate and display recipes
    st.subheader("🍴 Recipe Suggestions")
    try:
        recipes = generate_recipe_suggestions(ingredients)
        st.write(recipes)
    except Exception as e:
        st.error(f"Error generating recipes: {e}")

    # Generate and display substitutes
    st.subheader("🧑‍🍳 Ingredient Substitutions")
    for ingredient in ingredients:
        try:
            substitute = suggest_substitute(ingredient)
            st.markdown(f"**Substitute for {ingredient}:** {substitute}")
        except Exception as e:
            st.error(f"Error generating substitute for {ingredient}: {e}")

# Cooking tips section
st.subheader("✨ Cooking Tips and Tricks")
if st.button("Get a Cooking Tip"):
    try:
        tip = get_cooking_tip()
        st.write(tip)
    except Exception as e:
        st.error(f"Error fetching tip: {e}")

