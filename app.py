import streamlit as st
import pandas as pd
import re

# Load CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load HTML layout
def load_html():
    with open("index.html") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

# Apply CSS
load_css()

# Render HTML layout
load_html()

# App logic
df = pd.read_csv("food_recipes.csv")

# Display the title and description of the app
st.title("Virtual Recipe Suggestion App")
st.write("Find recipes based on the ingredients you have on hand!")

# Get user input for ingredients
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):")

# Your function to clean and find matching recipes
# Function and recipe matching code...
if user_ingredients:
    user_ingredients = [re.sub(r"\(.*?\)", "", ingredient).strip().lower() for ingredient in user_ingredients.split(",")]

    def clean_instructions(instruction_text):
        instruction_text = instruction_text.replace('|', '.')
        instruction_text = re.sub(r'\.\.+', '.', instruction_text)
        instruction_text = re.sub(r'\s+\.', '.', instruction_text)
        instruction_text = re.sub(r'\.\s*', '. ', instruction_text)
        instruction_text = '. '.join(sentence.strip().capitalize() for sentence in instruction_text.split('. '))
        return instruction_text.strip()

    def find_matching_recipes(user_ingredients, df):
        matching_recipes = []
        for _, row in df.iterrows():
            if isinstance(row['ingredients'], str):
                recipe_ingredients = row['ingredients'].split("|")
                recipe_ingredients = [re.sub(r"\(.*?\)", "", ingredient).strip().lower() for ingredient in recipe_ingredients]
            else:
                continue

            matches = []
            for user_ingredient in user_ingredients:
                if any(user_ingredient in recipe_ingredient for recipe_ingredient in recipe_ingredients):
                    matches.append(user_ingredient)

            match_count = len(matches)
            total_ingredients = len(recipe_ingredients)
            match_percentage = match_count / total_ingredients

            if match_percentage >= 0.5:
                missing_ingredients = [
                    recipe_ingredient for recipe_ingredient in recipe_ingredients
                    if not any(user_ingredient in recipe_ingredient for user_ingredient in user_ingredients)
                ]
                matching_recipes.append({
                    "title": row['recipe_title'],
                    "match_count": match_count,
                    "total_ingredients": total_ingredients,
                    "match_percentage": match_percentage,
                    "instructions": clean_instructions(row['instructions']),
                    "url": row['url'],
                    "missing_ingredients": missing_ingredients
                })

        matching_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
        return matching_recipes

    matching_recipes = find_matching_recipes(user_ingredients, df)
    if matching_recipes:
        for recipe in matching_recipes:
            st.write(f"**Recipe:** [{recipe['title']}]({recipe['url']})")
            st.write(f"**Matching Ingredients:** {recipe['match_count']} / {recipe['total_ingredients']} ({recipe['match_percentage']:.0%})")
            st.markdown(f"<div class='instructions'>{recipe['instructions']}</div>", unsafe_allow_html=True)
    else:
        st.write("No matching recipes found. Try different ingredients.")


