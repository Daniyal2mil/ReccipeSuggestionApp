import streamlit as st
from transformers import pipeline

# Load AI Model
@st.cache(allow_output_mutation=True)
def load_model():
    return pipeline('text-generation', model='gpt-2')

model = load_model()

# Streamlit UI
st.title("AI Recipe Suggestion App")
st.header("Input Ingredients")

# User Input
ingredients = st.text_area("Enter ingredients separated by commas")

if st.button("Generate Recipe"):
    if ingredients:
        prompt = f"Create a recipe using {ingredients}"
        result = model(prompt, max_length=200, num_return_sequences=1)
        st.subheader("Generated Recipe")
        st.write(result[0]['generated_text'])
    else:
        st.error("Please input ingredients!")
