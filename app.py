import streamlit as st
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# GPT-2 Model
@st.cache_resource
def load_gpt2_model():
    return pipeline("text-generation", model="distilgpt2", tokenizer="distilgpt2")

gpt2 = load_gpt2_model()

# Train Search Classifier
@st.cache_resource
def train_search_classifier():
    # Example dataset
    data = pd.DataFrame({
        "query": [
            "tomato, cheese, basil",  # Ingredients
            "How to make lasagna",  # Recipe query
            "onion, garlic, pepper",  # Ingredients
            "Pasta dishes",  # Recipe query
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

    # Train a Naive Bayes classifier
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
st.title("AI-Enhanced Recipe Generator 🍽️")
st.write("Enter your ingredients or recipe-related query to generate AI-enhanced suggestions!")

# Dropdown for user to explicitly choose search type
search_options = ["Search by Ingredients", "Search by Recipe"]
search_type_selection = st.selectbox("Choose search type:", search_options)

query = st.text_area(
    "Enter your query:",
    placeholder="e.g., tomato, cheese, basil or How to make lasagna"
)

if st.button("Generate Suggestions"):
    if query.strip():
        # Predict search type if user hasn't explicitly selected
        predicted_type = predict_search_type(query)
        st.write(f"Detected search type (based on query): **{predicted_type}**")
        st.write(f"Search type selected: **{search_type_selection}**")

        with st.spinner("Generating AI-enhanced output..."):
            # Generate GPT-2 Enhanced Content
            if search_type_selection == "Search by Ingredients":
                prompt = f"Create a recipe using these ingredients: {query}."
            else:  # "Search by Recipe"
                prompt = f"Write a detailed recipe guide for: {query}."
            
            gpt2_response = gpt2(prompt, max_length=150, num_return_sequences=1)
            st.subheader("AI-Generated Output:")
            st.markdown(gpt2_response[0]["generated_text"])
    else:
        st.error("Please enter a valid query.")







