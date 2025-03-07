import cv2
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_panel(image_path):
    """
    Analyze a comic panel image to detect figures, motion, and objects.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Dictionary containing analysis results:
            - figures: Number of figures/characters detected
            - motion: "action" or "static" based on edge density
            - objects: "sparks" or "none" based on edge intensity
    """
    try:
        # Load image in grayscale
        logger.info(f"Loading image from {image_path}")
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # Check if image was loaded successfully
        if img is None:
            logger.error(f"Failed to load image from {image_path}")
            # Return default values if image loading fails
            return {"figures": 1, "motion": "static", "objects": "none"}
        
        # Get image dimensions for logging
        height, width = img.shape
        logger.info(f"Image loaded successfully. Dimensions: {width}x{height}")
        
        # Apply Gaussian blur to reduce noise
        img_blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
        # Edge detection using Canny
        # Lower thresholds for comic art which often has strong lines
        edges = cv2.Canny(img_blurred, 80, 150)
        
        # Find contours for figure detection
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area to identify potential figures
        # Comic characters typically have substantial contour areas
        min_contour_area = 300  # Minimum area to be considered a figure
        figures = len([c for c in contours if cv2.contourArea(c) > min_contour_area])
        
        # If no figures detected, default to 1 (assume at least one character)
        if figures == 0:
            figures = 1
            
        logger.info(f"Detected {figures} figures in the image")
        
        # Determine if the scene is action or static based on edge density
        # More edges typically indicate more action
        edge_density = np.mean(edges) / 255.0  # Normalize to 0-1 range
        motion = "action" if edge_density > 0.04 else "static"  # Threshold determined empirically
        logger.info(f"Edge density: {edge_density:.4f}, Motion: {motion}")
        
        # Check for special objects like "sparks" based on edge intensity
        # High intensity edges in small areas often indicate effects like sparks
        edge_max = np.max(edges)
        edge_std = np.std(edges)
        objects = "sparks" if edge_max > 180 and edge_std > 40 else "none"
        logger.info(f"Edge max: {edge_max}, Edge std: {edge_std:.2f}, Objects: {objects}")
        
        return {
            "figures": figures,
            "motion": motion,
            "objects": objects
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        # Return default values in case of error
        return {"figures": 1, "motion": "static", "objects": "none"}
