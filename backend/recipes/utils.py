from collections import defaultdict

def generate_shopping_cart_txt(recipes):
    """Генерация TXT-файла со списком покупок."""
    
    ingredients = defaultdict(int)
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingr = recipe_ingredient.ingredient
            key = f'{ingr.name} ({ingr.measurement_unit})'
            ingredients[key] += recipe_ingredient.amount

    lines = []
    lines.append('Список покупок')
    lines.append('----------------')

    if not ingredients:
        lines.append('Ваш список покупок пуст.')
    else:
        for ingredient, amount in ingredients.items():
            lines.append(f'• {ingredient}: {amount}')
    
    content = '\n'.join(lines)
    return content

