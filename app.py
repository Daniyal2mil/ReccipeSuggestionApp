import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load DistilGPT2 Model
@st.cache_resource
def load_model():
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")  # DistilGPT2 for faster performance
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return model, tokenizer

model, tokenizer = load_model()

# Function to generate recipe based on recipe query
def generate_recipe(query):
    prompt = f"Write a complete recipe for: {query}. The recipe should include:\n" \
             f"1. A list of ingredients with exact measurements.\n" \
             f"2. Step-by-step instructions.\n" \
             f"3. Additional tips or variations to enhance the dish."

    # Encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate output
    output = model.generate(inputs, max_length=400, num_return_sequences=1, no_repeat_ngram_size=2, temperature=0.7)
    
    # Decode and return the generated text
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Streamlit App
st.title("AI Recipe Generator 🍴")
st.write("Enter a recipe query (e.g., 'How to make lasagna') to get a detailed AI-generated recipe!")

query = st.text_area("Enter your recipe query:", placeholder="e.g., How to make lasagna")

if st.button("Generate Recipe"):
    if query.strip():
        with st.spinner("Generating recipe..."):
            recipe = generate_recipe(query)
            st.subheader("AI-Generated Recipe:")
            st.markdown(recipe)
    else:
        st.error("Please enter a valid recipe query.")









