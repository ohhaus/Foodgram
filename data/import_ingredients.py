import json
from recipes.models import Ingredient

with open('ingredients.json', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for item in data:
    name = item.get("name")
    unit = item.get("measurement_unit")
    if name and unit:
        Ingredient.objects.get_or_create(name=name, measurement_unit=unit)
        count += 1

print(f"Импортировано {count} ингредиентов.")
