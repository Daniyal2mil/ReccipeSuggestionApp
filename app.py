# Load the AI Model
@st.cache_resource
def load_model():
    model_name = "EleutherAI/gpt-neo-1.3B"  # Open-source GPT-Neo model
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models")
    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir="./models")
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return generator, tokenizer

# Initialize the model and tokenizer
generator, tokenizer = load_model()

# Function to generate recipe suggestions
def generate_recipe_suggestions(ingredients):
    prompt = f"Suggest 3 recipes I can make using these ingredients: {', '.join(ingredients)}."
    response = generator(
        prompt,
        max_length=250,
        num_return_sequences=1,
        truncation=True,
        pad_token_id=tokenizer.eos_token_id,  # Set pad_token_id to eos_token_id
    )
    return response[0]["generated_text"]

# Function to suggest substitutes
def suggest_substitute(ingredient):
    prompt = f"What is a good substitute for {ingredient} in cooking?"
    response = generator(
        prompt,
        max_length=50,
        num_return_sequences=1,
        truncation=True,
        pad_token_id=tokenizer.eos_token_id,  # Set pad_token_id to eos_token_id
    )
    return response[0]["generated_text"]

# Function to generate cooking tips
def get_cooking_tip():
    prompt = "Give me a useful cooking tip for beginners."
    response = generator(
        prompt,
        max_length=100,
        num_return_sequences=1,
        truncation=True,
        pad_token_id=tokenizer.eos_token_id,  # Set pad_token_id to eos_token_id
    )
    return response[0]["generated_text"]

