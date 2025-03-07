import os
import logging
import requests
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextGen:
    """
    Text generation class that handles both Grok API and GPT-2 model.
    Prioritizes Grok API if a key is provided, with GPT-2 as fallback.
    """
    def __init__(self, grok_key=None):
        """
        Initialize the TextGen class.
        
        Args:
            grok_key (str, optional): Grok API key. If None, will use GPT-2 model.
        """
        self.grok_key = grok_key
        self.grok_url = "https://api.xai.com/grok/v1/generate"  # Update with actual endpoint
        
        # Only pre-load GPT-2 if no Grok key is provided
        if not grok_key:
            logger.info("No Grok API key provided - pre-loading GPT-2 model")
            try:
                self.gpt2 = pipeline("text-generation", model="distilgpt2", device=-1)  # Using smaller model
                logger.info("GPT-2 model initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing GPT-2 model: {str(e)}")
                self.gpt2 = None
        else:
            logger.info("Grok API key provided - will use API for text generation")
            self.gpt2 = None
    
    def generate(self, image_data, panel_num=1):
        """
        Generate a description for a comic panel based on image analysis data.
        
        Args:
            image_data (dict): Dictionary containing image analysis results
            panel_num (int, optional): Panel number. Defaults to 1.
            
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
        
        # Create prompt
        prompt = f"Panel {panel_num}: {figure_text} in {motion_text} scene{object_text}—comic style, short and wild!"
        
        # Try Grok API first if key is provided
        if self.grok_key:
            try:
                logger.info(f"Generating with Grok API. Prompt: {prompt}")
                headers = {
                    "Authorization": f"Bearer {self.grok_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "prompt": prompt,
                    "max_tokens": 30,
                    "temperature": 0.8
                }
                
                response = requests.post(
                    self.grok_url,
                    json=payload,
                    headers=headers,
                    timeout=5  # 5 second timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("text", "").strip()
                    logger.info(f"Grok API generated: {generated_text}")
                    
                    # Format the final description
                    if not generated_text.startswith(f"Panel {panel_num}:"):
                        description = f"Panel {panel_num}: {generated_text}"
                    else:
                        description = generated_text
                    
                    return description
                else:
                    logger.error(f"Grok API error: {response.status_code} - {response.text}")
                    # Fall back to GPT-2
            except Exception as e:
                logger.error(f"Error using Grok API: {str(e)} - falling back to GPT-2")
                # Fall back to GPT-2
        
        # Use GPT-2 as fallback
        logger.info(f"Generating with GPT-2. Prompt: {prompt}")
        
        # Load GPT-2 if not already loaded
        if not hasattr(self, "gpt2") or self.gpt2 is None:
            try:
                logger.info("Loading GPT-2 model on demand")
                self.gpt2 = pipeline("text-generation", model="distilgpt2", device=-1)
            except Exception as e:
                logger.error(f"Failed to load GPT-2 model: {str(e)}")
                return f"Panel {panel_num}: {figure_text} in {motion_text} scene{object_text}."
        
        try:
            result = self.gpt2(
                prompt,
                max_length=30,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
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
            
            # Format the final description
            if not completion:
                description = prompt
            elif not completion.startswith(f"Panel {panel_num}:"):
                description = f"Panel {panel_num}: {completion}"
            else:
                description = completion
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating text with GPT-2: {str(e)}")
            # Return a basic description based on image data as last resort
            return f"Panel {panel_num}: {figure_text} in {motion_text} scene{object_text}."

# Create a singleton instance with environment variable
GROK_API_KEY = os.environ.get('GROK_API_KEY', '')
text_generator = TextGen(grok_key=GROK_API_KEY if GROK_API_KEY else None)

def generate_description(image_data, panel_num):
    """
    Legacy function for backward compatibility.
    
    Args:
        image_data (dict): Dictionary containing image analysis results
        panel_num (int): Panel number
        
    Returns:
        str: Generated panel description
    """
    return text_generator.generate(image_data, panel_num)
