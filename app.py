import streamlit as st
import requests
import re
import streamlit.components.v1 as components
from huggingface_hub import InferenceClient

# Hugging Face Inference API details
HUGGINGFACE_API_KEY = "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"  # Replace with your Hugging Face API key
HF_MODEL = "gpt2"  # Using GPT-2 model for AI generation

# Initialize Hugging Face Inference Client
hf_client = InferenceClient(model=HF_MODEL, token=HUGGINGFACE_API_KEY)

# Spoonacular API details
API_URL = "https://api.spoonacular.com/recipes/findByIngredients"
API_KEY = "25d917fef9554ad3b05f732cd181a39f"  # Your Spoonacular API key

# Display the title and description of the app
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
st.markdown("""<style>
    body { font-family: 'Arial', sans-serif; background-color: #f4f8f4; color: #333; }
    .recipe-card { background-color: #fff; padding: 20px; margin-bottom: 20px; border-radius: 10px;
                   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); font-size: 1.1em; }
    .recipe-card img { width: 100%; height: auto; border-radius: 10px; margin-bottom: 10px; }
    .recipe-card a { text-decoration: none; color: #d97706; font-size: 1.2em; font-weight: bold; }
    .recipe-card a:hover { text-decoration: underline; }
    .header { text-align: center; font-size: 1.3em; font-weight: 500; margin-bottom: 20px; }
    .ingredient-list { color: #3c763d; font-weight: bold; }
    .match-percentage { color: #5bc0de; }
    .missing-ingredients { color: #d9534f; }
</style>""", unsafe_allow_html=True)

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
            "number": 50,
            "ranking": 1,
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching recipes: {e}")
            return []

    # Ingredient matching logic
    def exact_match(available, recipe_ingredient):
        return recipe_ingredient.lower() in available

    # Fetch recipes from Spoonacular
    recipes = fetch_recipes(user_ingredients)

    # Filter recipes with at least 30% match
    filtered_recipes = []
    for recipe in recipes:
        used_ingredients = [
            ing["name"]
            for ing in recipe["usedIngredients"]
            if exact_match(user_ingredients, ing["name"])
        ]
        missed_ingredients = [ing["name"] for ing in recipe["missedIngredients"]]
        total_ingredients = len(used_ingredients) + len(missed_ingredients)
        match_percentage = len(used_ingredients) / total_ingredients if total_ingredients > 0 else 0

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

    # Display filtered recipes
    if filtered_recipes:
        st.subheader("🍴 Recipes You Can Make:")
        for recipe in filtered_recipes:
            recipe_html = f"""
            <div class="recipe-card">
                <img src="{recipe['image']}" alt="{recipe['title']}">
                <h3><a href="{recipe['url']}" target="_blank">{recipe['title']}</a></h3>
                <p style="color: #4b9e47;">
                    <span class="ingredient-list">Matching Ingredients:</span> {recipe['match_count']} / {recipe['total_ingredients']} 
                    <span class="match-percentage">({recipe['match_percentage']:.0%})</span>
                </p>
                <p style="color: #4b9e47;">
                    <span class="ingredient-list">Available Ingredients:</span> {', '.join(recipe['available_ingredients'])}
                </p>
                <p style="color: #d9534f;">
                    <span class="missing-ingredients">Missing Ingredients:</span> {', '.join(recipe['missing_ingredients'])}
                </p>
            </div>
            """
            components.html(recipe_html, height=400)
    else:
        st.write("No matching recipes found. Try different ingredients.")

    # AI-powered recipe suggestion
    st.subheader("🧑‍🍳 AI-Generated Recipe Suggestion:")
    ai_prompt = f"Suggest a creative recipe using the following ingredients: {', '.join(user_ingredients)}."
    with st.spinner("Generating your recipe..."):
        try:
            # Using text_generation method correctly
            hf_response = hf_client.text_generation(inputs=ai_prompt, parameters={"max_length": 200})
            recipe = hf_response["generated_text"]
            st.markdown(f"**{recipe}**")
        except Exception as e:
            st.error(f"Error generating AI recipe: {e}")


