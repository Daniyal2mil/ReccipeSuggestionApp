import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load the DistilGPT2 Model
@st.cache_resource
def load_model():
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")  # DistilGPT2 for faster performance
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return model, tokenizer

model, tokenizer = load_model()

# Function to generate a detailed recipe from a query
def generate_recipe(query):
    # Refined prompt asking for more structured and detailed recipe generation
    prompt = f"Create a detailed, step-by-step recipe for {query}. Include precise measurements, specific cooking techniques, detailed instructions, and tips for preparing the dish. Make sure to describe the cooking process thoroughly, including prep times, cooking times, and serving suggestions."

    # Encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate the output with adjusted settings for more detail
    output = model.generate(inputs, 
                            max_length=500,  # Generate a more detailed response (up to 500 tokens)
                            num_return_sequences=1,  # Return one result
                            no_repeat_ngram_size=2,  # Prevent repetition in the text
                            temperature=0.7,  # Keep it creative but focused
                            top_p=0.9,  # Ensure diversity in the output
                            top_k=50)  # Narrow down sampling for relevance

    # Decode the generated text and strip the prompt from the beginning
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Remove the prompt part from the beginning of the generated text
    recipe = generated_text.replace(f"Create a detailed, step-by-step recipe for {query}. Include precise measurements, specific cooking techniques, detailed instructions, and tips for preparing the dish. Make sure to describe the cooking process thoroughly, including prep times, cooking times, and serving suggestions.", "").strip()

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






