from collections import defaultdict
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_shopping_cart_pdf(recipes):
    """Генерация PDF-файла со списком покупок."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    try:
        pdfmetrics.registerFont(
            TTFont(
                'DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            )
        )
        font_name = 'DejaVuSans'
    except Exception:
        font_name = 'Helvetica'

    p.setFont(font_name, 16)
    p.drawString(50, height - 50, 'Список покупок')

    ингредиенты = defaultdict(int)

    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingr = recipe_ingredient.ingredient
            ключ = f'{ingr.name} ({ingr.measurement_unit})'
            ингредиенты[ключ] += recipe_ingredient.amount

    y_position = height - 100
    p.setFont(font_name, 12)

    for ingr, amount in ингредиенты.items():
        if y_position < 50:
            p.showPage()
            y_position = height - 50
            p.setFont(font_name, 12)

        строка = f'• {ingr}: {amount}'
        try:
            p.drawString(50, y_position, строка)
        except UnicodeEncodeError:
            строка_ascii = строка.encode('ascii', 'ignore').decode('ascii')
            p.drawString(50, y_position, строка_ascii)

        y_position -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()
