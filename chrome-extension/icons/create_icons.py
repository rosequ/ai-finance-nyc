#!/usr/bin/env python3
"""
Simple script to create basic icons for the Chrome extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with text"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(0, 123, 255, 255),  # Blue background
                outline=(0, 86, 179, 255),  # Darker blue border
                width=2)
    
    # Try to use a font, fallback to default if not available
    try:
        font_size = size // 3
        font = ImageFont.truetype("Arial.ttf", font_size)
    except:
        try:
            font_size = size // 3
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Add text
    text = "T&C"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2
    
    # Draw text with shadow
    draw.text((x+1, y+1), text, fill=(0, 0, 0, 100), font=font)  # Shadow
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)  # Main text
    
    # Save icon
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icon sizes"""
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        filename = f"icon-{size}.png"
        create_icon(size, filename)
    
    print("All icons created successfully!")
    print("\nTo use these icons:")
    print("1. The icons are already referenced in manifest.json")
    print("2. If you want better icons, replace these PNG files")
    print("3. Keep the same filenames: icon-16.png, icon-32.png, icon-48.png, icon-128.png")

if __name__ == "__main__":
    main()
