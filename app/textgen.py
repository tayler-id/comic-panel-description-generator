import os
import logging
import requests
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if we should use Grok API
USE_GROK_API = os.environ.get('USE_GROK_API', 'false').lower() == 'true'
GROK_API_KEY = os.environ.get('GROK_API_KEY', '')

# Initialize GPT-2 model (lazy loading - will only load when needed)
_generator = None

def get_generator():
    """
    Lazy-load the GPT-2 model to avoid loading it if Grok API is used
    """
    global _generator
    if _generator is None:
        logger.info("Initializing GPT-2 model for text generation")
        try:
            _generator = pipeline("text-generation", model="gpt2", device=-1)
            logger.info("GPT-2 model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing GPT-2 model: {str(e)}")
            raise
    return _generator

def generate_with_grok(prompt):
    """
    Generate text using Grok API
    """
    if not GROK_API_KEY:
        logger.warning("Grok API key not provided, falling back to GPT-2")
        return generate_with_gpt2(prompt)
    
    try:
        logger.info(f"Generating text with Grok API. Prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "max_tokens": 30,  # Reduced for more concise descriptions
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.grok.ai/v1/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            logger.error(f"Grok API error: {response.status_code} - {response.text}")
            return generate_with_gpt2(prompt)
        
        result = response.json()
        generated_text = result.get("choices", [{}])[0].get("text", "")
        logger.info(f"Grok API generated: {generated_text}")
        
        return generated_text.strip()
    
    except Exception as e:
        logger.error(f"Error using Grok API: {str(e)}")
        return generate_with_gpt2(prompt)

def generate_with_gpt2(prompt):
    """
    Generate text using local GPT-2 model
    """
    try:
        logger.info(f"Generating text with GPT-2. Prompt: {prompt}")
        generator = get_generator()
        
        result = generator(
            prompt,
            max_length=30,  # Reduced for more concise descriptions
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            top_k=40,  # Added to reduce weird outputs
            do_sample=True
        )
        
        generated_text = result[0]["generated_text"]
        
        # Extract just the completion part (remove the prompt)
        completion = generated_text[len(prompt):].strip()
        
        # Take the first sentence or the whole text if it's short
        if "." in completion:
            completion = completion.split(".")[0] + "."
        
        # Clean up unwanted artifacts like file paths
        completion = completion.replace("C:/", "").replace("\\", "").strip()
        
        logger.info(f"GPT-2 generated: {completion}")
        return completion
    
    except Exception as e:
        logger.error(f"Error generating text with GPT-2: {str(e)}")
        return f"Description unavailable: {str(e)}"

def generate_description(image_data, panel_num):
    """
    Generate a description for a comic panel based on image analysis data
    
    Args:
        image_data (dict): Dictionary containing image analysis results
        panel_num (int): Panel number
        
    Returns:
        str: Generated panel description
    """
    # Extract data from image analysis
    figures = image_data.get("figures", 1)
    motion = image_data.get("motion", "static")
    objects = image_data.get("objects", "none")
    
    # Create a prompt based on the image data
    figure_text = f"{figures} character{'s' if figures > 1 else ''}"
    motion_text = "an action-packed" if motion == "action" else "a static"
    object_text = " with sparks flying" if objects == "sparks" else ""
    
    # Enhanced prompts for better comic-style descriptions
    if USE_GROK_API:
        prompt = f"Panel {panel_num}: {figure_text} in {motion_text} scene{object_text}—comic style, short and wild!"
    else:
        prompt = f"Panel {panel_num}: {figure_text} in {motion_text} scene{object_text}—comic book action!"
    
    # Generate text using either Grok API or GPT-2
    if USE_GROK_API:
        generated_text = generate_with_grok(prompt)
    else:
        generated_text = generate_with_gpt2(prompt)
    
    # Format the final description
    if not generated_text.startswith(f"Panel {panel_num}:"):
        description = f"Panel {panel_num}: {generated_text}"
    else:
        description = generated_text
    
    return description
