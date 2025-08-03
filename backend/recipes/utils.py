from collections import defaultdict
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_shopping_cart_pdf(recipes):
    """Генерация PDF-файла со списком покупок."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Используем стандартный шрифт Times-Roman
    font_name = 'Times-Roman'

    # Стили для текста
    styles = {
        'Title': ParagraphStyle(
            'Title',
            fontName=font_name,
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # По центру
            leading=30  # Межстрочный интервал
        ),
        'Normal': ParagraphStyle(
            'Normal',
            fontName=font_name,
            fontSize=14,
            spaceAfter=10,
            leftIndent=20,
            leading=20  # Межстрочный интервал
        )
    }

    # Сбор ингредиентов
    ingredients = defaultdict(int)
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingr = recipe_ingredient.ingredient
            key = f'{ingr.name} ({ingr.measurement_unit})'
            ingredients[key] += recipe_ingredient.amount

    # Формирование документа
    story = []
    
    # Заголовок
    story.append(Paragraph('Список покупок', styles['Title']))
    story.append(Spacer(1, 12))

    # Список ингредиентов
    for ingr, amount in ingredients.items():
        text = f'• {ingr}: {amount}'
        story.append(Paragraph(text, styles['Normal']))

    # Генерация PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
