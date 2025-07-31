"""
Utility functions for recipes app.
"""
from collections import defaultdict
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch


def generate_shopping_cart_pdf(recipes):
    """Generate PDF with shopping cart ingredients."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Try to register a font that supports Cyrillic
    try:
        # This is a basic approach - in production you'd want to include proper fonts
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        font_name = 'DejaVuSans'
    except:
        # Fallback to Helvetica if DejaVu is not available
        font_name = 'Helvetica'
    
    # Title
    p.setFont(font_name, 16)
    p.drawString(50, height - 50, "Список покупок")
    
    # Collect all ingredients with their amounts
    ingredients_dict = defaultdict(int)
    
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingredient = recipe_ingredient.ingredient
            key = f"{ingredient.name} ({ingredient.measurement_unit})"
            ingredients_dict[key] += recipe_ingredient.amount
    
    # Draw ingredients list
    y_position = height - 100
    p.setFont(font_name, 12)
    
    for ingredient, amount in ingredients_dict.items():
        if y_position < 50:  # Start new page if needed
            p.showPage()
            y_position = height - 50
            p.setFont(font_name, 12)
        
        text = f"• {ingredient}: {amount}"
        try:
            p.drawString(50, y_position, text)
        except UnicodeEncodeError:
            # Fallback for non-ASCII characters
            text_ascii = text.encode('ascii', 'ignore').decode('ascii')
            p.drawString(50, y_position, text_ascii)
        
        y_position -= 20
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

