import streamlit as st
from transformers import pipeline

# Load the AI model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="gpt2", tokenizer="gpt2")

model = load_model()

# App title
st.title("AI Recipe Generator 🍳")
st.write("Enter ingredients, and the AI will suggest a recipe for you!")

# User input
ingredients = st.text_area("List your ingredients (comma-separated):", placeholder="e.g., chicken, garlic, onions")

# Generate recipe button
if st.button("Generate Recipe"):
    if ingredients.strip():
        prompt = f"Create a recipe using these ingredients: {ingredients}. Provide a recipe name, ingredients list, and step-by-step instructions."
        with st.spinner("Generating recipe..."):
            recipe = model(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
            st.subheader("Here is your AI-generated recipe:")
            st.write(recipe)
    else:
        st.error("Please enter some ingredients!")

# Footer
st.markdown("---")
st.markdown("Powered by [GPT-2](https://huggingface.co/gpt2)")

