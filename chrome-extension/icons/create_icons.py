#!/usr/bin/env python3
"""
Create simple placeholder icons for the Chrome extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the specified size"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#007cff')
    draw = ImageDraw.Draw(img)
    
    # Draw a white circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
    
    # Try to add text (📋 emoji or "TC")
    try:
        # Try to use a system font
        if size >= 32:
            font_size = size // 3
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = "📋" if size >= 48 else "TC"
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, fill='#007cff', font=font)
    except:
        # If font loading fails, just draw a simple shape
        center = size // 2
        rect_size = size // 4
        draw.rectangle([center-rect_size//2, center-rect_size//2, 
                       center+rect_size//2, center+rect_size//2], 
                      fill='#007cff')
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icon sizes"""
    icon_dir = os.path.dirname(os.path.abspath(__file__))
    
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        filename = os.path.join(icon_dir, f"icon-{size}.png")
        create_icon(size, filename)
    
    print("✅ All icons created successfully!")

if __name__ == "__main__":
    main()
