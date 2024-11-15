import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Display the title and description of the app with emoji
st.title("🍲 Virtual Recipe Suggestion App")
st.markdown(
    """
    <p style="text-align: center; font-size: 1.2em;">
        Find recipes based on the ingredients you have on hand! 🍳
    </p>
    """,
    unsafe_allow_html=True,
)

# Add lime green styling for all body text
st.markdown("""
    <style>
        body {
            color: limegreen;
        }
        .recipe-card p {
            color: limegreen;
        }
    </style>
""", unsafe_allow_html=True)



# Get user input for ingredients
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):")

if user_ingredients:
    # Convert user input to a list of ingredients
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in user_ingredients.split(",")
    ]

    # Function to clean and format instructions
    def clean_instructions(instruction_text):
        # Replace '|' with a period to act as a sentence delimiter
        instruction_text = instruction_text.replace('|', '.')
        
        # Fix multiple periods and space formatting issues
        instruction_text = re.sub(r'\.\.+', '.', instruction_text)  # Replace multiple dots with a single dot
        instruction_text = re.sub(r'\s+\.', '.', instruction_text)  # Remove space before periods
        instruction_text = re.sub(r'\.\s*', '. ', instruction_text)  # Ensure single space after each period

        # Capitalize the first letter of each sentence
        instruction_text = '. '.join(
            sentence.strip().capitalize() for sentence in instruction_text.split('. ')
        )

        return instruction_text.strip()

    # Function to find recipes that match user's ingredients with at least 50% match
    def find_matching_recipes(user_ingredients, df):
        matching_recipes = []
        
        for _, row in df.iterrows():
            # Ensure the ingredients field is a string before splitting
            if isinstance(row['ingredients'], str):
                recipe_ingredients = row['ingredients'].split("|")
                
                # Remove text within parentheses for each ingredient and convert to lowercase
                recipe_ingredients = [
                    re.sub(r"\(.*?\)", "", ingredient).strip().lower()
                    for ingredient in recipe_ingredients
                ]
            else:
                continue

            # Calculate matching ingredients
            matches = []
            for user_ingredient in user_ingredients:
                # Check if any recipe ingredient contains the user ingredient as a substring
                if any(user_ingredient in recipe_ingredient for recipe_ingredient in recipe_ingredients):
                    matches.append(user_ingredient)

            match_count = len(matches)
            total_ingredients = len(recipe_ingredients)
            match_percentage = match_count / total_ingredients

            # Only include recipes with at least 50% matching ingredients
            if match_percentage >= 0.5:
                # Find missing ingredients more precisely
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

        # Sort recipes by the percentage of matching ingredients, descending
        matching_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return matching_recipes

    # Find recipes and display them with custom HTML
    matching_recipes = find_matching_recipes(user_ingredients, df)
    
    if matching_recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in matching_recipes:
            recipe_html = f"""
            <div class="recipe-card">
                <h3><a href="{recipe['url']}" target="_blank">{recipe['title']}</a></h3>
                <p><strong>Matching Ingredients:</strong> {recipe['match_count']} / {recipe['total_ingredients']} ({recipe['match_percentage']:.0%})</p>
                <p><strong>Missing Ingredients:</strong> {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}</p>
                <p><strong>Instructions:</strong> {recipe['instructions']}</p>
            </div>
            """
            components.html(recipe_html, height=300)
    else:
        st.write("No matching recipes found. Try different ingredients.")


