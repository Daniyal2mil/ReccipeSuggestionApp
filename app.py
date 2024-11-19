import streamlit as st
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

# Load GPT-Neo Model
@st.cache_resource
def load_model():
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")  # 1.3B version
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return model, tokenizer

model, tokenizer = load_model()

# Function to generate recipe using GPT-Neo
def generate_recipe(query):
    prompt = f"Create a detailed recipe using the following ingredients: {query}. Please include a list of ingredients, step-by-step instructions, and serving suggestions."

    # Encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate output
    output = model.generate(inputs, max_length=300, num_return_sequences=1, no_repeat_ngram_size=2, temperature=0.7)
    
    # Decode and return the generated text
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Streamlit App
st.title("AI Recipe Generator 🍴")
st.write("Enter your ingredients or a recipe query, and get a detailed AI-generated recipe!")

query = st.text_area("Enter your ingredients:", placeholder="e.g., tomato, cheese, basil or How to make lasagna")

if st.button("Generate Recipe"):
    if query.strip():
        with st.spinner("Generating recipe..."):
            recipe = generate_recipe(query)
            st.subheader("AI-Generated Recipe:")
            st.markdown(recipe)
    else:
        st.error("Please enter a valid query.")









