import streamlit as st
import requests
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import joblib

# Spoonacular API Setup
SPOONACULAR_API_KEY = "25d917fef9554ad3b05f732cd181a39f"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="distilgpt2", tokenizer="distilgpt2")

gpt2 = load_gpt2_model()

# Train AI Model
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
        "number": 3,
        "ranking": 1,
        "diet": diet_preference if diet_preference != "None" else "",
        "apiKey": SPOONACULAR_API_KEY,
    }
    response = requests.get(SPOONACULAR_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching recipes from Spoonacular API")
        return []

# Streamlit App
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients or search by a normal query to get recipe suggestions, enhanced by AI!")

query = st.text_area("Enter your query:", placeholder="e.g., tomato, cheese, basil or Pasta dishes")
diet_choices = ["None", "Vegetarian", "Vegan", "Gluten-Free", "Paleo", "Keto"]
diet_preference = st.selectbox("Select dietary preference:", diet_choices)

if st.button("Generate Recipes"):
    if query.strip():
        search_type = predict_search_type(query)
        st.write(f"Detected search type: **{search_type}**")

        with st.spinner("Fetching recipes..."):
            if search_type == "ingredients":
                recipes = fetch_recipes(query, diet_preference)
                if recipes:
                    for recipe in recipes:
                        st.markdown(f"### {recipe['title']}")
                        st.image(recipe.get("image", ""), width=300)

                        # Enhance with GPT-2
                        prompt = f"Generate a detailed recipe for {recipe['title']} using ingredients: {query}."
                        gpt2_response = gpt2(prompt, max_length=150, num_return_sequences=1)
                        st.markdown(gpt2_response[0]["generated_text"])
                else:
                    st.error("No recipes found!")
            else:
                st.write("This feature for normal queries is under development!")
    else:
        st.error("Please enter a valid query.")





