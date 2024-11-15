import streamlit as st
import requests
import re
import streamlit.components.v1 as components

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  

# Display the title and description of the app with emoji
st.title("🍲 Virtual Recipe Suggestion App")
st.markdown(
    """
    <p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #3c763d;">
        Find recipes based on the ingredients you have on hand! 🍳
    </p>
    """,
    unsafe_allow_html=True,
)

# Add styling for all body text, cards, and recipe elements
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f8f4;
            color: #333;
        }
        .recipe-card {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-size: 1.1em;
        }
        .recipe-card img {
            width: 100%;
            height: auto;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .recipe-card a {
            text-decoration: none;
            color: #d97706;
            font-size: 1.2em;
            font-weight: bold;
        }
        .recipe-card a:hover {
            text-decoration: underline;
        }
        .recipe-card p {
            color: #555;
        }
        .header {
            text-align: center;
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 20px;
        }
        .ingredient-list {
            color: #3c763d;
            font-weight: bold;
        }
        .match-percentage {
            color: #5bc0de;
        }
        .missing-ingredients {
            color: #d9534f;
        }
        .input-box {
            width: 100%;
            padding: 10px;
            font-size: 1.1em;
            border-radius: 8px;
            border: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .input-box:focus {
            border-color: #3c763d;
            outline: none;
        }
    </style>
""", unsafe_allow_html=True)

# Get user input for ingredients
user_ingredients = st.text_input(
    "Enter the ingredients you have (comma-separated):",
    key="ingredients_input",
    placeholder="e.g., Buttermilk, Chicken, Paprika",
    help="Type ingredients you have at home to find recipes.",
    max_chars=200,
    label_visibility="visible",
)

if user_ingredients:
    # Convert user input to a cleaned list of ingredients
    user_ingredients = [
        re.sub(r"\(.*?\)", "", ingredient).strip().lower()
        for ingredient in re.split(r",\s*|,\s*", user_ingredients)  # Split on commas and handle extra spaces
        if ingredient.strip()  # Ignore empty entries
    ]

    # Fetch recipes using Spoonacular API
    def fetch_recipes(ingredients):
        params = {
            "ingredients": ",".join(ingredients),
            "apiKey": API_KEY,
            "number": 20,  # Number of recipes to return
            "ranking": 1,  # Prioritize matching ingredients
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()  # Check for HTTP errors
            return response.json()  # Spoonacular returns JSON data
        except requests.RequestException as e:
            if response.status_code == 401:
                st.error("Invalid API key. Please check your Spoonacular API key.")
            elif response.status_code == 402:
                st.error("API rate limit exceeded. Upgrade your Spoonacular plan.")
            else:
                st.error(f"Error fetching recipes: {e}")
            return []
        except ValueError:
            st.error("Invalid API response: Unable to parse JSON.")
            return []

    # Process recipes to ensure all relevant matches are included
    def filter_and_sort_recipes(recipes, ingredients):
        filtered_recipes = []
        for recipe in recipes:
            # Identify matching and missing ingredients
            used_ingredients = [
                ing["name"]
                for ing in recipe["usedIngredients"]
                if ing["name"].lower() in ingredients
            ]
            missed_ingredients = [ing["name"] for ing in recipe["missedIngredients"]]
            total_ingredients = len(used_ingredients) + len(missed_ingredients)
            match_percentage = len(used_ingredients) / total_ingredients if total_ingredients > 0 else 0

            # Include recipe if at least 30% of ingredients match
            if match_percentage >= 0.3:
                filtered_recipes.append(
                    {
                        "title": recipe["title"],
                        "url": f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-').lower()}-{recipe['id']}",
                        "image": recipe.get("image", ""),
                        "match_count": len(used_ingredients),
                        "total_ingredients": total_ingredients,
                        "match_percentage": match_percentage,
                        "available_ingredients": used_ingredients,
                        "missing_ingredients": missed_ingredients,
                    }
                )

        # Sort recipes by match percentage and then by count of matched ingredients
        filtered_recipes.sort(
            key=lambda x: (x["match_percentage"], x["match_count"]), reverse=True
        )
        return filtered_recipes

    # Fetch and process recipes
    recipes = fetch_recipes(user_ingredients)
    filtered_recipes = filter_and_sort_recipes(recipes, user_ingredients)

    if filtered_recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in filtered_recipes:
            # Display each recipe card
            recipe_html = f"""
            <div class="recipe-card">
                <img src="{recipe['image']}" alt="{recipe['title']}">
                <h3><a href="{recipe['url']}" target="_blank">{recipe['title']}</a></h3>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="ingredient-list">Matching Ingredients:</span> {recipe['match_count']} / {recipe['total_ingredients']} 
                    <span class="match-percentage">({recipe['match_percentage']:.0%})</span>
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="ingredient-list">Available Ingredients:</span> {', '.join(recipe['available_ingredients']) if recipe['available_ingredients'] else 'None'}
                </p>
                <p style="color: #4b9e47; font-size: 1.1em;">
                    <span class="missing-ingredients">Missing Ingredients:</span> {', '.join(recipe['missing_ingredients']) if recipe['missing_ingredients'] else 'None'}
                </p>
            </div>
            """
            components.html(recipe_html, height=400)
    else:
        st.write("No matching recipes found. Try different ingredients.")
