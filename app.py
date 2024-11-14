import streamlit as st
import pandas as pd
import re

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Display the HTML and CSS files within the app
with open("index.html", "r") as file:
    st.markdown(file.read(), unsafe_allow_html=True)

# Get user input for ingredients
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):")

if user_ingredients:
    # Convert user input to a list of ingredients, ignoring parentheses
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in user_ingredients.split(",")
    ]

    # Function to clean and format instructions
    def clean_instructions(instruction_text):
        instruction_text = instruction_text.replace('|', '.')
        instruction_text = re.sub(r'\.\.+', '.', instruction_text)
        instruction_text = re.sub(r'\s+\.', '.', instruction_text)
        instruction_text = re.sub(r'\.\s*', '. ', instruction_text)
        instruction_text = '. '.join(
            sentence.strip().capitalize() for sentence in instruction_text.split('. ')
        )
        return instruction_text.strip()

    # Function to find recipes based on user ingredients
    def find_matching_recipes(user_ingredients, df):
        matching_recipes = []
        for _, row in df.iterrows():
            if isinstance(row['ingredients'], str):
                recipe_ingredients = row['ingredients'].split("|")
                recipe_ingredients = [
                    re.sub(r"\(.*?\)", "", ingredient).strip().lower()
                    for ingredient in recipe_ingredients
                ]
            else:
                continue

            matches = [user_ingredient for user_ingredient in user_ingredients if any(user_ingredient in ingredient for ingredient in recipe_ingredients)]
            match_percentage = len(matches) / len(recipe_ingredients)

            if match_percentage >= 0.5:
                missing_ingredients = [ingredient for ingredient in recipe_ingredients if not any(user_ingredient in ingredient for user_ingredient in user_ingredients)]
                matching_recipes.append({
                    "title": row['recipe_title'],
                    "instructions": clean_instructions(row['instructions']),
                    "url": row['url'],
                    "missing_ingredients": missing_ingredients
                })
        return matching_recipes

    # Find matching recipes
    matching_recipes = find_matching_recipes(user_ingredients, df)

    # Display matching recipes
    if matching_recipes:
        for recipe in matching_recipes:
            st.write(f"**Recipe:** [{recipe['title']}]({recipe['url']})")
            st.write(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}")
            st.write(f"**Instructions:** {recipe['instructions']}")
            st.write("---")
    else:
        st.write("No matching recipes found.")

