"""
A simple script to test hot-reloading in the Docker container.

This script makes a request to the API server's health endpoint to verify it's running,
then makes a request to the analyze endpoint with a test image.

Usage:
    python test_hot_reload.py
"""

import requests
import time
import os
import base64

def test_health():
    """Test the health endpoint of the API server."""
    try:
        response = requests.get('http://localhost:8081/api/health')
        if response.status_code == 200:
            print("API server is running!")
            return True
        else:
            print(f"API server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to API server. Is it running?")
        return False

def test_analyze():
    """Test the analyze endpoint of the API server with a test image."""
    # Check if the test image exists
    test_image = 'comic_sketch.png'
    if not os.path.exists(test_image):
        print(f"Test image {test_image} not found.")
        return False
    
    # Read the test image
    with open(test_image, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Make the request
    try:
        response = requests.post(
            'http://localhost:8081/api/analyze',
            json={'image_data': image_data, 'is_path': False, 'panel_num': 1}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Analysis result:")
            print(f"  Figures: {result.get('figures', 'unknown')}")
            print(f"  Motion: {result.get('motion', 'unknown')}")
            print(f"  Objects: {result.get('objects', 'unknown')}")
            return True
        else:
            print(f"API server returned status code {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to API server. Is it running?")
        return False

def main():
    """Main function."""
    print("Testing hot-reloading in Docker container...")
    
    # Wait for the API server to start
    print("Waiting for API server to start...")
    for _ in range(10):
        if test_health():
            break
        time.sleep(1)
    else:
        print("API server did not start within 10 seconds.")
        return
    
    # Test the analyze endpoint
    print("\nTesting analyze endpoint...")
    test_analyze()
    
    print("\nTest complete!")
    print("You can now make changes to the code and see them reflected without rebuilding the Docker container.")
    print("For example, try modifying app/vision.py to change how figures are detected.")

if __name__ == '__main__':
    main()
