"""Image processing utilities for the Comic Panel MCP Server."""

import base64
import cv2
import numpy as np
import logging

logger = logging.getLogger("comic-mcp-server")

def load_image(image_data, is_path=True):
    """
    Load an image from a file path or base64 encoded data.
    
    Args:
        image_data (str): File path or base64 encoded image data
        is_path (bool): Whether image_data is a file path (True) or base64 encoded image (False)
        
    Returns:
        numpy.ndarray: Loaded image
        
    Raises:
        ValueError: If the image cannot be loaded
    """
    try:
        if is_path:
            # Load from file path
            img = cv2.imread(image_data, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"Failed to load image from path: {image_data}")
            return img
        else:
            # Load from base64 encoded data
            img_data = base64.b64decode(image_data)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode base64 image data")
            return img
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        raise

def image_to_base64(img):
    """
    Convert an image to base64 encoded string.
    
    Args:
        img (numpy.ndarray): Image to convert
        
    Returns:
        str: Base64 encoded image
    """
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

def detect_figures(img):
    """
    Detect figures (characters) in an image.
    
    Args:
        img (numpy.ndarray): Image to analyze
        
    Returns:
        list: List of detected figures with bounding boxes
    """
    height, width = img.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 100, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size and shape
    figures = []
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 2000:  # Minimum area threshold
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Calculate solidity (area / convex hull area)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # Filter by aspect ratio and solidity
            if 0.2 < aspect_ratio < 5 and solidity > 0.1:
                figures.append({
                    "id": i,
                    "type": "character",
                    "bbox": [x, y, w, h],
                    "area": area,
                    "center": [x + w//2, y + h//2]
                })
    
    # Apply sanity checks
    if not figures:
        # Default to one character covering the whole image
        figures.append({
            "id": 0,
            "type": "character",
            "bbox": [0, 0, width, height],
            "area": width * height,
            "center": [width//2, height//2]
        })
    
    return figures

def detect_motion(img):
    """
    Detect motion in an image.
    
    Args:
        img (numpy.ndarray): Image to analyze
        
    Returns:
        dict: Motion information
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 100, 200)
    
    # Calculate edge density and distribution
    edge_density = np.mean(edges) / 255.0
    edge_std = np.std(edges) / 255.0
    
    # Determine motion type
    is_action = edge_density > 0.08 and edge_std > 0.2
    
    return {
        "type": "action" if is_action else "static",
        "edge_density": float(edge_density),
        "edge_std": float(edge_std)
    }

def detect_objects(img):
    """
    Detect special objects (like sparks) in an image.
    
    Args:
        img (numpy.ndarray): Image to analyze
        
    Returns:
        dict: Object information
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Calculate edge statistics
    edges = cv2.Canny(blurred, 100, 200)
    edge_max = np.max(edges)
    edge_std = np.std(edges)
    
    # Threshold for bright regions
    _, binary = cv2.threshold(blurred, 220, 255, cv2.THRESH_BINARY)
    
    # Find small bright regions
    bright_contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    small_bright_regions = [c for c in bright_contours if 10 < cv2.contourArea(c) < 100]
    
    # Determine if sparks are present
    has_sparks = edge_max > 220 and edge_std > 60 and len(small_bright_regions) >= 3
    
    return {
        "type": "sparks" if has_sparks else "none",
        "count": len(small_bright_regions) if has_sparks else 0
    }
