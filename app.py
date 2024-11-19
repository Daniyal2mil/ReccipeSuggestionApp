import streamlit as st
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# LLaMA Model for Recipe Generation
@st.cache_resource
def load_llama_model():
    return pipeline("text-generation", model="meta-llama/LLaMA-2-7b-hf", tokenizer="meta-llama/LLaMA-2-7b-hf")

llama = load_llama_model()

# Train Search Classifier
@st.cache_resource
def train_search_classifier():
    # Example dataset for training
    data = pd.DataFrame({
        "query": [
            "tomato, cheese, basil",  # Ingredients
            "chocolate cake recipe",  # Recipe search
            "onion, garlic, pepper",  # Ingredients
            "how to make lasagna",  # Recipe search
        ],
        "label": ["ingredients", "recipe", "ingredients", "recipe"],
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

# Streamlit App
st.title("LLaMA Recipe Generator 🍴")
st.write("Enter your ingredients or a recipe-related query to generate recipes with AI!")

query = st.text_area("Enter your query:", placeholder="e.g., tomato, cheese, basil or Pasta dishes")

if st.button("Generate Recipes"):
    if query.strip():
        search_type = predict_search_type(query)
        st.write(f"Detected search type: **{search_type}**")

        with st.spinner("Generating recipes..."):
            if search_type == "ingredients":
                # Generate recipes using ingredients
                prompt = f"Create three recipes using these ingredients: {query}."
                llama_response = llama(prompt, max_length=150, num_return_sequences=3)
                st.subheader("AI-Generated Recipes:")
                for idx, response in enumerate(llama_response, 1):
                    st.markdown(f"### Recipe {idx}")
                    st.markdown(response["generated_text"])
            else:
                # Generate recipe for a dish
                prompt = f"Provide a detailed recipe for {query}."
                llama_response = llama(prompt, max_length=200, num_return_sequences=1)
                st.subheader("AI-Generated Recipe:")
                st.markdown(llama_response[0]["generated_text"])
    else:
        st.error("Please enter a valid query.")






