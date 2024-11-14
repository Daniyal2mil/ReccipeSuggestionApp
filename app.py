import streamlit as st
import pandas as pd
import re

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Display the title and description of the app
st.title("Virtual Recipe Suggestion App")
st.write("Find recipes based on the ingredients you have on hand!")

# Get user input for ingredients
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):")

if user_ingredients:
    # Convert user input to a list of ingredients, ignoring parentheses
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in user_ingredients.split(",")
    ]

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
                # Find missing ingredients for better feedback
                missing_ingredients = set(recipe_ingredients) - set(matches)
                matching_recipes.append({
                    "title": row['recipe_title'],
                    "match_count": match_count,
                    "total_ingredients": total_ingredients,
                    "match_percentage": match_percentage,
                    "instructions": row['instructions'],
                    "url": row['url'],
                    "missing_ingredients": missing_ingredients
                })

        # Sort recipes by the percentage of matching ingredients, descending
        matching_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return matching_recipes

    # Find recipes and display them
    matching_recipes = find_matching_recipes(user_ingredients, df)
    
    if matching_recipes:
        st.subheader("Recipes you can make:")
        for recipe in matching_recipes:
            st.write(f"**Recipe:** [{recipe['title']}]({recipe['url']})")
            st.write(f"**Matching Ingredients:** {recipe['match_count']} / {recipe['total_ingredients']} ({recipe['match_percentage']:.0%})")
            st.write(f"**Missing Ingredients:** {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}")
            
            # Split the instructions by "|" and format as bullet points
            st.write("**Instructions:**")
            instructions = recipe['instructions'].split("|")
            for step in instructions:
                st.write(f"- {step.strip()}")
            st.write("---")
    else:
        st.write("No matching recipes found. Try different ingredients.")
