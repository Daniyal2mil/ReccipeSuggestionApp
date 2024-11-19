import re
import streamlit as st
from transformers import pipeline

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="gpt2", tokenizer="gpt2")

gpt2 = load_gpt2_model()

# Function to clean and format GPT-2 output
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
st.title("AI-Enhanced Recipe Generator with Preferences 🍽️")
st.write("Enter your ingredients and dietary preferences to get AI-generated recipes!")

# Input for ingredients
ingredients = st.text_area("Enter ingredients (comma-separated):", placeholder="e.g., tomato, cheese, basil")

dietary_preferences = st.selectbox(
    "Select a dietary preference:",
    ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Paleo"]
)

if st.button("Generate Recipes"):
    if ingredients.strip():
        st.subheader("Recipes based on your ingredients and preferences:")

        # Process input ingredients
        ingredient_list = [i.strip().lower() for i in ingredients.split(",") if i.strip()]

        # AI-based recipe generation
        prompt = (
            f"Generate a detailed recipe for a {dietary_preferences.lower()} dish using the ingredients: {', '.join(ingredient_list)}. "
            "Include a title, the ingredients (categorizing as available or missing), and clear instructions."
        )

        with st.spinner("Generating AI-based recipes..."):
            raw_ai_recipe = gpt2(prompt, max_length=300, num_return_sequences=1)[0]["generated_text"]

        # Clean and format output
        formatted_recipe = clean_and_format_gpt2_output(raw_ai_recipe)

        # Display the AI-enhanced recipe
        st.markdown(formatted_recipe, unsafe_allow_html=True)

        # Analyze ingredients
        ai_ingredients_section = re.search(r"Ingredients:\n(.*?)(\n\n|$)", formatted_recipe, re.DOTALL)
        if ai_ingredients_section:
            ai_ingredients = [
                item.strip().lower()
                for item in re.split(r"[\n,]", ai_ingredients_section.group(1))
                if item.strip()
            ]

            available = [ing for ing in ai_ingredients if ing in ingredient_list]
            missing = [ing for ing in ai_ingredients if ing not in ingredient_list]

            st.markdown("**Available Ingredients:**")
            st.write(", ".join(available) if available else "None")

            st.markdown("**Missing Ingredients:**")
            st.write(", ".join(missing) if missing else "None")
    else:
        st.error("Please enter some ingredients!")




