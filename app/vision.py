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
        # Adjusted thresholds for better edge detection in comics
        edges = cv2.Canny(img_blurred, 100, 200)
        
        # Find contours for figure detection
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Improved figure detection with better filtering
        # Significantly increased minimum area to avoid counting small details as figures
        min_contour_area = 2000  # Increased from 300 to 2000
        
        # Additional filtering for contours that are likely to be characters
        filtered_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_area:
                # Calculate aspect ratio and solidity as additional filters
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = float(w) / h if h > 0 else 0
                hull = cv2.convexHull(c)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Character contours typically have reasonable aspect ratios and solidity
                if 0.2 < aspect_ratio < 5 and solidity > 0.1:
                    filtered_contours.append(c)
        
        # Count figures with a reasonable upper limit for comic panels
        figures = len(filtered_contours)
        
        # Apply a sanity check - most comic panels have 1-5 characters
        if figures > 5:
            logger.warning(f"Detected unusually high figure count ({figures}), capping at 5")
            figures = min(figures, 5)
        
        # If no figures detected, default to 1 (assume at least one character)
        if figures == 0:
            figures = 1
            
        logger.info(f"Detected {figures} figures in the image")
        
        # Improved motion detection with adjusted threshold
        # Comic panels typically have high edge density even in static scenes
        edge_density = np.mean(edges) / 255.0  # Normalize to 0-1 range
        
        # Additional check for motion: look at the distribution of edges
        # Action scenes typically have more varied edge distribution
        edge_std_normalized = np.std(edges) / 255.0
        
        # Combined criteria for action detection
        is_action = edge_density > 0.08 and edge_std_normalized > 0.2
        motion = "action" if is_action else "static"
        
        logger.info(f"Edge density: {edge_density:.4f}, Edge std normalized: {edge_std_normalized:.4f}, Motion: {motion}")
        
        # Improved object detection with more specific criteria for sparks
        # Sparks have very specific visual characteristics
        edge_max = np.max(edges)
        edge_std = np.std(edges)
        
        # Check for small, bright regions that could be sparks
        # Count small, high-intensity regions
        _, binary = cv2.threshold(img_blurred, 220, 255, cv2.THRESH_BINARY)
        spark_contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        small_bright_regions = len([c for c in spark_contours if 10 < cv2.contourArea(c) < 100])
        
        # More specific criteria for sparks
        has_sparks = edge_max > 220 and edge_std > 60 and small_bright_regions >= 3
        objects = "sparks" if has_sparks else "none"
        
        logger.info(f"Edge max: {edge_max}, Edge std: {edge_std:.2f}, Small bright regions: {small_bright_regions}, Objects: {objects}")
        
        return {
            "figures": figures,
            "motion": motion,
            "objects": objects
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        # Return default values in case of error
        return {"figures": 1, "motion": "static", "objects": "none"}
