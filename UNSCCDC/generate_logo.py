from PIL import Image, ImageDraw, ImageFont

# Set the size and colors
size = (500, 500)
navy = (0, 31, 63)     # Professional Navy
orange = (230, 81, 0)  # Uganda Digital Orange
white = (255, 255, 255)

# Create the image
img = Image.new('RGBA', size, (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw the Outer Shield/Circle
draw.ellipse([10, 10, 490, 490], fill=navy, outline=orange, width=15)
draw.ellipse([30, 30, 470, 470], outline=white, width=2)

# Draw a Digital Symbol (A stylized sun/gear for control)
for i in range(0, 360, 30):
    draw.pieslice([150, 150, 350, 350], start=i, end=i+15, fill=orange)

# Draw the Center Circle
draw.ellipse([180, 180, 320, 320], fill=navy, outline=white, width=3)

# Add the Text
try:
    # If you have a font file, use it. Otherwise, it uses default.
    draw.text((115, 370), "UNSCCDC", fill=orange, font=None)
except:
    draw.text((200, 240), "UNSCCDC", fill=orange)

# Save it directly into your static folder
import os
path = "static/admin_custom/logo.png"
os.makedirs(os.path.dirname(path), exist_ok=True)
img.save(path)
print(f"Success! Logo generated at {path}")