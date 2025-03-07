from PIL import Image, ImageDraw
import os

# Create a new white image
width, height = 600, 400
image = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(image)

# Draw a stick figure
# Head
draw.ellipse((270, 70, 330, 130), outline='black', width=3)

# Body
draw.line((300, 130, 300, 250), fill='black', width=3)

# Arms
draw.line((300, 170, 250, 200), fill='black', width=3)
draw.line((300, 170, 350, 200), fill='black', width=3)

# Legs
draw.line((300, 250, 270, 320), fill='black', width=3)
draw.line((300, 250, 330, 320), fill='black', width=3)

# Eyes
draw.ellipse((285, 90, 295, 100), outline='black', width=3)
draw.ellipse((305, 90, 315, 100), outline='black', width=3)

# Smile
draw.arc((285, 100, 315, 120), 0, 180, fill='black', width=3)

# Ensure the uploads directory exists
os.makedirs('app/uploads', exist_ok=True)

# Save the image
image.save('comic_sketch.png')

print("Comic sketch created successfully: comic_sketch.png")
