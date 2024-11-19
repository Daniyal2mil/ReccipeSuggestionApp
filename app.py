import streamlit as st
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# Load Flan-T5 Model
@st.cache_resource
def load_text_generation_model():
    # Use Hugging Face's Flan-T5
    return pipeline("text2text-generation", model="google/flan-t5-base", tokenizer="google/flan-t5-base")

text_generator = load_text_generation_model()

# Train Search Classifier
@st.cache_resource
def train_search_classifier():
    # Improved dataset with more variation
    data = pd.DataFrame({
        "query": [
            "tomato, cheese, basil",  # Ingredients
            "How to make lasagna",  # Recipe query
            "chicken, garlic, pepper",  # Ingredients
            "Biryani recipe",  # Recipe query
            "apple, cinnamon, sugar",  # Ingredients
            "Steps to bake a chocolate cake",  # Recipe query
        ],
        "label": ["ingredients", "recipe", "ingredients", "recipe", "ingredients", "recipe"],
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
        # Predict search type using classifier
        predicted_type = predict_search_type(query)
        
        # Use the user's explicit selection as the final search type
        final_search_type = "ingredients" if search_type_selection == "Search by Ingredients" else "recipe"

        # Feedback on detected and selected search type
        st.write(f"Detected search type: **{predicted_type}**")
        st.write(f"Final search type (based on selection): **{final_search_type}**")

        with st.spinner("Generating AI-enhanced output..."):
            # Generate Enhanced Content with Flan-T5
            if final_search_type == "ingredients":
                prompt = (
                    f"Using only the ingredients: {query}, write a clear and detailed recipe with:\n"
                    f"1. A list of ingredients with quantities.\n"
                    f"2. Step-by-step preparation instructions.\n"
                    f"3. Serving suggestions."
                )
            else:  # "recipe"
                prompt = (
                    f"Write a comprehensive recipe for: {query}. Include:\n"
                    f"1. A detailed list of ingredients with measurements.\n"
                    f"2. Clear, step-by-step cooking instructions.\n"
                    f"3. Cooking tips for best results."
                )
            
            # Generate response with Flan-T5
            response = text_generator(prompt, max_length=200)
            generated_text = response[0]["generated_text"]

            # Validate and display output
            if len(generated_text.strip()) < 50 or "recipe" not in generated_text.lower():
                st.error("The generated text seems incomplete or irrelevant. Please try again with a clearer query.")
            else:
                st.subheader("AI-Generated Recipe Output:")
                st.markdown(generated_text)
    else:
        st.error("Please enter a valid query.")










