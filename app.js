// This is a mock function to simulate finding recipes based on user input.
function findRecipes() {
    const userIngredients = document.getElementById('user-ingredients').value.toLowerCase().split(',').map(ingredient => ingredient.trim());

    // Example of static data; in real-world, you might fetch this from an API or your backend.
    const recipes = [
        {
            title: 'Tomato Soup',
            url: '#',
            ingredients: ['tomato', 'onion', 'garlic'],
            instructions: 'Boil tomatoes, blend them with onions and garlic.',
            missingIngredients: ['salt']
        },
        {
            title: 'Cheese Sandwich',
            url: '#',
            ingredients: ['bread', 'cheese', 'butter'],
            instructions: 'Toast the bread, melt the cheese, and assemble.',
            missingIngredients: ['lettuce']
        }
    ];

    const recipesSection = document.getElementById('recipes-section');
    recipesSection.innerHTML = ''; // Clear any existing recipes

    // Find recipes that match at least 50% of user ingredients
    recipes.forEach(recipe => {
        const matchingIngredients = recipe.ingredients.filter(ingredient => userIngredients.includes(ingredient));
        const matchPercentage = matchingIngredients.length / recipe.ingredients.length;

        if (matchPercentage >= 0.5) {
            const recipeCard = document.createElement('div');
            recipeCard.className = 'recipe-card';
            recipeCard.innerHTML = `
                <h3><a href="${recipe.url}">${recipe.title}</a></h3>
                <p><strong>Matching Ingredients:</strong> ${matchingIngredients.length} / ${recipe.ingredients.length} (${(matchPercentage * 100).toFixed(0)}%)</p>
                <p><strong>Missing Ingredients:</strong> ${recipe.missingIngredients.join(', ')}</p>
                <p><strong>Instructions:</strong> ${recipe.instructions}</p>
            `;
            recipesSection.appendChild(recipeCard);
        }
    });
}
