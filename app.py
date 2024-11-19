import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load the DistilGPT2 Model
@st.cache_resource
def load_model():
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")  # DistilGPT2 for faster performance
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return model, tokenizer

model, tokenizer = load_model()

# Function to generate a full recipe from a query
def generate_recipe(query):
    # Simplified prompt to guide the model without including instructions in the output
    prompt = f"Generate a detailed recipe for {query}. Include ingredients, instructions, and any tips."

    # Encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate the output with better settings to ensure a more detailed response
    output = model.generate(inputs, 
                            max_length=400,  # Generate up to 400 tokens for a fuller recipe
                            num_return_sequences=1,  # Return one result
                            no_repeat_ngram_size=2,  # Prevent repetition in the text
                            temperature=0.7,  # Control randomness
                            top_p=0.9,  # Ensure diverse outputs by sampling from top 90% likely words
                            top_k=50)  # Narrow down the sampling to top 50 choices for speed and relevance

    # Decode the generated text and strip the prompt from the beginning
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Remove the prompt part from the beginning of the generated text
    recipe = generated_text.replace(f"Generate a detailed recipe for {query}. Include ingredients, instructions, and any tips.", "").strip()

    return recipe

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






