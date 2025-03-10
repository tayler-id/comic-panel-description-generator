import os
import logging
import requests
import json
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiProviderTextGen:
    """
    Enhanced text generation class that supports multiple API providers with fallback chain.
    Prioritizes API calls over local models to avoid memory constraints.
    """
    def __init__(self, config=None):
        """
        Initialize the MultiProviderTextGen class.
        
        Args:
            config (dict, optional): Configuration options including API priority.
        """
        # Load API keys from environment variables
        self.openai_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.grok_key = os.environ.get('GROK_API_KEY', '')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.google_key = os.environ.get('GOOGLE_API_KEY', '')
        self.hf_key = os.environ.get('HUGGINGFACE_API_KEY', '')
        
        # API endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        self.grok_url = "https://api.xai.com/v1/chat/completions"  # Update with actual endpoint
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"  # Update with actual endpoint
        self.hf_inference_url = "https://api-inference.huggingface.co/models/"
        
        # Default priority order (can be configured)
        self.config = config or {}
        self.priority = self.config.get('priority', ['openai', 'anthropic', 'grok', 'deepseek', 'huggingface', 'rule_based'])
        
        # Log available APIs
        self._log_available_apis()
        
        # Only pre-load local model if no API keys are available
        if not any([self.openai_key, self.anthropic_key, self.grok_key, self.deepseek_key, self.hf_key]):
            logger.info("No API keys provided - will use local model as fallback")
            try:
                self.local_model = pipeline("text-generation", model="distilgpt2", device=-1)
                logger.info("Local model initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing local model: {str(e)}")
                self.local_model = None
        else:
            logger.info("API keys provided - will use APIs for text generation")
            self.local_model = None
    
    def _log_available_apis(self):
        """Log which APIs are available based on provided keys."""
        apis = []
        if self.openai_key:
            apis.append("OpenAI")
        if self.anthropic_key:
            apis.append("Anthropic")
        if self.grok_key:
            apis.append("Grok")
        if self.deepseek_key:
            apis.append("DeepSeek")
        if self.hf_key:
            apis.append("HuggingFace")
        
        if apis:
            logger.info(f"Available APIs: {', '.join(apis)}")
        else:
            logger.warning("No API keys provided - will rely on local model or rule-based generation")
    
    def _create_prompt(self, image_data, panel_num=1):
        """
        Create a prompt based on image analysis data.
        
        Args:
            image_data (dict): Dictionary containing image analysis results
            panel_num (int, optional): Panel number. Defaults to 1.
            
        Returns:
            str: Formatted prompt
        """
        # Extract data from image analysis
        figures = image_data.get("figures", 1)
        motion = image_data.get("motion", "static")
        objects = image_data.get("objects", "none")
        
        # Create a more descriptive and accurate prompt based on the image data
        figure_text = f"{figures} character{'s' if figures > 1 else ''}"
        
        # More nuanced description of motion
        if motion == "action":
            motion_text = "a dynamic"
            motion_detail = "showing movement and energy"
        else:
            motion_text = "a calm"
            motion_detail = "with minimal movement"
        
        # More specific object description
        if objects == "sparks":
            object_text = " with visual effects like sparks or impact lines"
        else:
            object_text = ""
        
        # Create a more detailed prompt that focuses on accurate description
        # rather than exaggerated action
        base_prompt = (
            f"Panel {panel_num}: Describe ONLY what is objectively visible in this comic panel with {figure_text} in {motion_text} scene{object_text}. "
            f"The scene is {motion_detail}. Describe ONLY the physical elements that are definitely present: "
            f"character positions, visible objects, and panel composition. "
            f"If speech bubbles are present, ONLY mention their existence - DO NOT invent their contents unless text is clearly visible. "
            f"DO NOT make assumptions about emotions, thoughts, or narrative context. "
            f"Keep the description minimal, factual, and focused only on what can be seen."
        )
        
        return base_prompt
    
    def _format_description(self, generated_text, panel_num):
        """
        Format the generated text into a consistent panel description.
        Apply post-processing to remove speculative language and ensure factual content.
        
        Args:
            generated_text (str): Raw generated text
            panel_num (int): Panel number
            
        Returns:
            str: Formatted panel description
        """
        # Clean up the text
        clean_text = generated_text.strip()
        
        # Remove any file paths or unwanted artifacts
        clean_text = clean_text.replace("C:/", "").replace("\\", "")
        
        # Ensure it starts with "Panel X:"
        if not clean_text.startswith(f"Panel {panel_num}:"):
            clean_text = f"Panel {panel_num}: {clean_text}"
        
        # Apply post-processing to remove speculative language
        clean_text = self._remove_speculative_language(clean_text)
        
        return clean_text
    
    def _remove_speculative_language(self, text):
        """
        Remove speculative language and ensure the description is factual.
        
        Args:
            text (str): Description text
            
        Returns:
            str: Cleaned description text
        """
        # List of speculative phrases to remove or replace
        speculative_phrases = [
            # Phrases that suggest dialogue content
            (r'saying "[^"]*"', "with a speech bubble"),
            (r'says "[^"]*"', "has a speech bubble"),
            (r'reads "[^"]*"', "contains text"),
            (r'exclaims "[^"]*"', "has a speech bubble"),
            (r'thinking "[^"]*"', "is present"),
            
            # Phrases that suggest emotions or thoughts
            (r'appears to be (feeling|thinking|considering)', "is"),
            (r'seems to be (happy|sad|angry|excited|nervous|worried|concerned|thinking)', "is"),
            (r'looks (happy|sad|angry|excited|nervous|worried|concerned)', "is visible"),
            
            # Phrases that suggest narrative context
            (r'is about to', "is"),
            (r'is going to', "is"),
            (r'is trying to', "is"),
            (r'is planning to', "is"),
            (r'has just', "is"),
            (r'had just', "is"),
            
            # Phrases that suggest interpretation
            (r'probably', ""),
            (r'possibly', ""),
            (r'perhaps', ""),
            (r'maybe', ""),
            (r'might be', "is"),
            (r'could be', "is"),
            (r'would be', "is"),
            (r'appears to be', "is"),
            (r'seems to be', "is"),
            (r'looks like', "shows"),
        ]
        
        # Apply replacements
        import re
        for pattern, replacement in speculative_phrases:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _generate_with_openai(self, prompt):
        """
        Generate text using OpenAI API.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with OpenAI API. Prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a comic panel describer that ONLY states what is objectively visible. NEVER invent dialogue content, emotions, or scene details. If you see a speech bubble, only mention its presence - NEVER guess what's written inside unless the text is clearly legible. Describe only physical elements that are definitely present in the image. Do not make assumptions about what characters are thinking or feeling unless their expressions are extremely clear. Do not use interpretive language - stick to physical descriptions only. Your descriptions must be factual enough to charge money for."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.5
        }
        
        response = requests.post(
            self.openai_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"].strip()
            logger.info(f"OpenAI generated: {generated_text}")
            return generated_text
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _generate_with_anthropic(self, prompt):
        """
        Generate text using Anthropic API.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with Anthropic API. Prompt: {prompt}")
        
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "claude-instant-1.2",
            "max_tokens": 50,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            self.anthropic_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result["content"][0]["text"].strip()
            logger.info(f"Anthropic generated: {generated_text}")
            return generated_text
        else:
            logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
            raise Exception(f"Anthropic API error: {response.status_code}")
    
    def _generate_with_grok(self, prompt):
        """
        Generate text using Grok API.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with Grok API. Prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {self.grok_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            self.grok_url,
            json=payload,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"].strip()
            logger.info(f"Grok API generated: {generated_text}")
            return generated_text
        else:
            logger.error(f"Grok API error: {response.status_code} - {response.text}")
            raise Exception(f"Grok API error: {response.status_code}")
    
    def _generate_with_deepseek(self, prompt):
        """
        Generate text using DeepSeek API.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with DeepSeek API. Prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            self.deepseek_url,
            json=payload,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"].strip()
            logger.info(f"DeepSeek API generated: {generated_text}")
            return generated_text
        else:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
            raise Exception(f"DeepSeek API error: {response.status_code}")
    
    def _generate_with_huggingface(self, prompt):
        """
        Generate text using HuggingFace Inference API.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with HuggingFace API. Prompt: {prompt}")
        
        headers = {
            "Authorization": f"Bearer {self.hf_key}",
            "Content-Type": "application/json"
        }
        
        # Use a model suitable for text generation
        model = "gpt2"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 50,
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        response = requests.post(
            f"{self.hf_inference_url}{model}",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result[0]["generated_text"]
            # Extract just the completion part (remove the prompt)
            completion = generated_text[len(prompt):].strip()
            logger.info(f"HuggingFace generated: {completion}")
            return completion
        else:
            logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
            raise Exception(f"HuggingFace API error: {response.status_code}")
    
    def _generate_with_local_model(self, prompt):
        """
        Generate text using local model.
        
        Args:
            prompt (str): The prompt to send to the model
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating with local model. Prompt: {prompt}")
        
        # Load model if not already loaded
        if not hasattr(self, "local_model") or self.local_model is None:
            try:
                logger.info("Loading local model on demand")
                self.local_model = pipeline("text-generation", model="distilgpt2", device=-1)
            except Exception as e:
                logger.error(f"Failed to load local model: {str(e)}")
                raise Exception("Failed to load local model")
        
        result = self.local_model(
            prompt,
            max_length=50,
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
        
        logger.info(f"Local model generated: {completion}")
        return completion
    
    def _generate_rule_based(self, image_data, panel_num):
        """
        Generate a description using rule-based approach (no ML/API).
        
        Args:
            image_data (dict): Dictionary containing image analysis results
            panel_num (int): Panel number
            
        Returns:
            str: Generated panel description
        """
        logger.info("Generating with rule-based approach")
        
        # Extract data from image analysis
        figures = image_data.get("figures", 1)
        motion = image_data.get("motion", "static")
        objects = image_data.get("objects", "none")
        
        # Build minimal, factual description based on rules
        description = f"Panel {panel_num}: "
        
        # Character description - just state the count
        if figures == 1:
            description += "One character visible"
        elif figures == 2:
            description += "Two characters visible"
        else:
            description += f"{figures} characters visible"
        
        # Scene description - just state if there's motion
        if motion == "action":
            description += " in a scene with movement"
        else:
            description += " in a static scene"
        
        # Object description - only if definitely present
        if objects == "sparks":
            description += " with visual effects"
        
        # End with period
        if not description.endswith("."):
            description += "."
        
        logger.info(f"Rule-based generated: {description}")
        return description
    
    def generate(self, image_data, panel_num=1):
        """
        Generate a description for a comic panel based on image analysis data.
        Tries each provider in priority order, falling back to the next if one fails.
        
        Args:
            image_data (dict): Dictionary containing image analysis results
            panel_num (int, optional): Panel number. Defaults to 1.
            
        Returns:
            str: Generated panel description
        """
        prompt = self._create_prompt(image_data, panel_num)
        
        # Try each provider in priority order
        for provider in self.priority:
            try:
                if provider == 'openai' and self.openai_key:
                    generated_text = self._generate_with_openai(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'anthropic' and self.anthropic_key:
                    generated_text = self._generate_with_anthropic(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'grok' and self.grok_key:
                    generated_text = self._generate_with_grok(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'deepseek' and self.deepseek_key:
                    generated_text = self._generate_with_deepseek(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'huggingface' and self.hf_key:
                    generated_text = self._generate_with_huggingface(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'local_model' and hasattr(self, 'local_model') and self.local_model is not None:
                    generated_text = self._generate_with_local_model(prompt)
                    return self._format_description(generated_text, panel_num)
                
                elif provider == 'rule_based':
                    return self._generate_rule_based(image_data, panel_num)
                
            except Exception as e:
                logger.error(f"Error with {provider}: {str(e)}")
                continue
        
        # Ultimate fallback if all providers fail
        logger.warning("All providers failed, using basic fallback")
        return f"Panel {panel_num}: Comic scene with {image_data.get('figures', 1)} character(s)."

# Create a singleton instance with environment variables
text_generator = MultiProviderTextGen()

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
