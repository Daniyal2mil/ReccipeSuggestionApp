import streamlit as st
import pandas as pd

# Load the recipe dataset
df = pd.read_csv("food_recipes.csv")

# Display the title and description of the app
st.title("Virtual Recipe Suggestion App")
st.write("Find recipes based on the ingredients you have on hand!")

# Get user input for ingredients
user_ingredients = st.text_input("Enter the ingredients you have (comma-separated):")

if user_ingredients:
    # Convert user input to a list of ingredients
    user_ingredients = [ingredient.strip().lower() for ingredient in user_ingredients.split(",")]

    # Function to find recipes that match user's ingredients
    def find_matching_recipes(user_ingredients, df):
        matching_recipes = []
        for _, row in df.iterrows():
            # Ensure the ingredients field is a string before splitting
            if isinstance(row['ingredients'], str):
                recipe_ingredients = row['ingredients'].split("|")
                recipe_ingredients = [ingredient.strip().lower() for ingredient in recipe_ingredients]
            else:
                # Skip this row if ingredients are missing or not a string
                continue

            # Calculate how many ingredients match
            matches = set(user_ingredients).intersection(set(recipe_ingredients))
            match_count = len(matches)
            
            if match_count > 0:  # Only include recipes with at least one matching ingredient
                matching_recipes.append((row['recipe_title'], match_count, row['instructions'], row['url']))

        # Sort recipes by the number of matching ingredients, descending
        matching_recipes.sort(key=lambda x: x[1], reverse=True)
        
        return matching_recipes

    # Find recipes and display them
    matching_recipes = find_matching_recipes(user_ingredients, df)
    
    if matching_recipes:
        st.subheader("Recipes you can make:")
        for recipe in matching_recipes:
            st.write(f"**Recipe:** [{recipe[0]}]({recipe[3]})")
            st.write(f"**Matching Ingredients Count:** {recipe[1]}")
            st.write(f"**Instructions:** {recipe[2]}")
            st.write("---")
    else:
        st.write("No matching recipes found. Try different ingredients.")
