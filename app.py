import streamlit as st
import requests
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# Spoonacular API Setup
SPOONACULAR_API_KEY = "25d917fef9554ad3b05f732cd181a39f"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="distilgpt2", tokenizer="distilgpt2")

gpt2 = load_gpt2_model()

# Train Search Classifier
@st.cache_resource
def train_search_classifier():
    # Example dataset for training
    data = pd.DataFrame({
        "query": [
            "tomato, cheese, basil",  # Ingredients
            "chocolate cake recipe",  # Normal search
            "onion, garlic, pepper",  # Ingredients
            "how to make lasagna",  # Normal search
        ],
        "label": ["ingredients", "normal", "ingredients", "normal"],
    })

    X = data["query"]
    y = data["label"]

    # Vectorize text data
    vectorizer = CountVectorizer()
    X_vectorized = vectorizer.fit_transform(X)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

    # Train a simple Naive Bayes classifier
    classifier = MultinomialNB()
    classifier.fit(X_train, y_train)

    # Evaluate model
    y_pred = classifier.predict(X_test)
    st.write(f"Classifier Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    return vectorizer, classifier

vectorizer, classifier = train_search_classifier()

# Function to predict search type
def predict_search_type(query):
    query_vectorized = vectorizer.transform([query])
    return classifier.predict(query_vectorized)[0]

# Function to get recipes from Spoonacular
@st.cache
def fetch_recipes(ingredients, diet_preference):
    params = {
        "ingredients": ingredients,
        "number": 3,  # Limit the number of recipes
        "ranking": 1,
        "diet": diet_preference.lower() if diet_preference != "None" else "",
        "apiKey": SPOONACULAR_API_KEY,
    }

    try:
        response = requests.get(SPOONACULAR_URL, params=params)
        if response.status_code == 200:
            recipes = response.json()
            if recipes:
                return recipes
            else:
                st.warning("No recipes found for the given ingredients and dietary preferences.")
                return []
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

# Streamlit App
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients or a normal query to get recipe suggestions, enhanced by AI!")

query = st.text_area("Enter your query:", placeholder="e.g., tomato, cheese, basil or Pasta dishes")
diet_choices = ["None", "Vegetarian", "Vegan", "Gluten-Free", "Paleo", "Keto"]
diet_preference = st.selectbox("Select dietary preference:", diet_choices)

if st.button("Generate Recipes"):
    if query.strip():
        search_type = predict_search_type(query)
        st.write(f"Detected search type: **{search_type}**")

        with st.spinner("Fetching recipes..."):
            if search_type == "ingredients":
                # Fetch recipes
                recipes = fetch_recipes(query, diet_preference)
                if recipes:
                    st.subheader("Recipes Found:")
                    for recipe in recipes:
                        st.markdown(f"### {recipe.get('title', 'Untitled')}")
                        st.image(recipe.get("image", "https://via.placeholder.com/300"), width=300)

                        # Generate GPT-2 Enhanced Recipe
                        prompt = f"Generate a detailed recipe for {recipe['title']} using ingredients: {query}."
                        gpt2_response = gpt2(prompt, max_length=150, num_return_sequences=1)
                        st.markdown("**AI-Enhanced Recipe**")
                        st.markdown(gpt2_response[0]["generated_text"])
                else:
                    st.error("No recipes found.")
            else:
                st.write("Normal search type is under development.")
    else:
        st.error("Please enter a valid query.")










