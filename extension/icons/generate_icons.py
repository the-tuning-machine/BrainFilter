"""
Génère des icônes simples pour l'extension.
Nécessite Pillow: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    """Crée une icône simple avec un emoji cerveau."""
    # Créer une image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleur de fond (bleu)
    draw.ellipse([0, 0, size-1, size-1], fill='#1a73e8')

    # Texte (emoji ou initiale)
    try:
        # Essayer d'utiliser une police système
        font_size = int(size * 0.5)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        # Fallback sur la police par défaut
        font = ImageFont.load_default()

    # Dessiner "B" pour BrainFilter
    text = "B"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill='white', font=font)

    return img

def main():
    """Génère les 3 tailles d'icônes."""
    sizes = [16, 48, 128]

    for size in sizes:
        print(f"Génération de l'icône {size}x{size}...")
        icon = create_icon(size)
        icon.save(f'icon{size}.png')
        print(f"  ✓ icon{size}.png créé")

    print("\n✓ Toutes les icônes ont été créées !")

if __name__ == "__main__":
    main()
