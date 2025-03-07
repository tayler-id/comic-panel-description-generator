import os
import sys
from vision import analyze_panel
from textgen import generate_description

def main():
    # Path to the comic sketch image
    image_path = '/app/uploads/comic_sketch.png'
    
    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)
    
    print(f"Processing image: {image_path}")
    
    try:
        # Analyze the panel using the vision module
        print("Analyzing panel...")
        image_data = analyze_panel(image_path)
        print(f"Analysis results: {image_data}")
        
        # Generate description using the textgen module
        print("Generating description...")
        panel_num = 1  # For MVP, we assume a single panel
        description = generate_description(image_data, panel_num)
        
        print("\n--- Generated Panel Description ---")
        print(description)
        print("-----------------------------------")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
