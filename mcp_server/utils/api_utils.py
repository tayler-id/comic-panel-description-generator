"""API utilities for the Comic Panel MCP Server."""

import os
import json
import logging
import requests

logger = logging.getLogger("comic-mcp-server")

class MultiProviderAPI:
    """Class for handling API calls to multiple providers with fallback."""
    
    def __init__(self):
        """Initialize the API handler with available API keys."""
        # Load API keys from environment variables
        self.keys = {
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
            "grok": os.environ.get("GROK_API_KEY", ""),
            "deepseek": os.environ.get("DEEPSEEK_API_KEY", "")
        }
        
        # Default priority order (can be configured)
        self.priority = ["openai", "anthropic", "grok", "deepseek"]
        
        # Log available APIs
        apis = [api for api, key in self.keys.items() if key]
        if apis:
            logger.info(f"Available APIs: {', '.join(apis)}")
        else:
            logger.warning("No API keys provided")
    
    def call_openai(self, system_prompt, user_prompt, model="gpt-3.5-turbo", max_tokens=150, temperature=0.5):
        """
        Call the OpenAI API.
        
        Args:
            system_prompt (str): System prompt
            user_prompt (str): User prompt
            model (str): Model to use
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for sampling
            
        Returns:
            str: Generated text
            
        Raises:
            Exception: If the API call fails
        """
        if not self.keys["openai"]:
            raise ValueError("OpenAI API key not provided")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.keys['openai']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.info(f"Calling OpenAI API with model {model}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def call_anthropic(self, prompt, model="claude-instant-1.2", max_tokens=150, temperature=0.7):
        """
        Call the Anthropic API.
        
        Args:
            prompt (str): Prompt
            model (str): Model to use
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for sampling
            
        Returns:
            str: Generated text
            
        Raises:
            Exception: If the API call fails
        """
        if not self.keys["anthropic"]:
            raise ValueError("Anthropic API key not provided")
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.keys["anthropic"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature
        }
        
        logger.info(f"Calling Anthropic API with model {model}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"].strip()
        else:
            error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def call_grok(self, prompt, max_tokens=150, temperature=0.7):
        """
        Call the Grok API.
        
        Args:
            prompt (str): Prompt
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for sampling
            
        Returns:
            str: Generated text
            
        Raises:
            Exception: If the API call fails
        """
        if not self.keys["grok"]:
            raise ValueError("Grok API key not provided")
        
        # Note: This is a placeholder for the Grok API endpoint
        url = "https://api.xai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.keys['grok']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.info("Calling Grok API")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = f"Grok API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def call_deepseek(self, prompt, model="deepseek-chat", max_tokens=150, temperature=0.7):
        """
        Call the DeepSeek API.
        
        Args:
            prompt (str): Prompt
            model (str): Model to use
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for sampling
            
        Returns:
            str: Generated text
            
        Raises:
            Exception: If the API call fails
        """
        if not self.keys["deepseek"]:
            raise ValueError("DeepSeek API key not provided")
        
        # Note: This is a placeholder for the DeepSeek API endpoint
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.keys['deepseek']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.info(f"Calling DeepSeek API with model {model}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def generate_description(self, image_analysis, panel_num=1):
        """
        Generate a description using multiple providers with fallback.
        
        Args:
            image_analysis (dict): Image analysis data
            panel_num (int): Panel number
            
        Returns:
            str: Generated description
        """
        # Extract data from image analysis
        figures = len(image_analysis.get("figures", []))
        motion_type = image_analysis.get("motion", {}).get("type", "static")
        object_type = image_analysis.get("objects", {}).get("type", "none")
        
        # Create prompt
        figure_text = f"{figures} character{'s' if figures > 1 else ''}"
        motion_text = "a dynamic" if motion_type == "action" else "a calm"
        motion_detail = "showing movement and energy" if motion_type == "action" else "with minimal movement"
        object_text = " with visual effects like sparks or impact lines" if object_type == "sparks" else ""
        
        prompt = (
            f"Panel {panel_num}: Describe ONLY what is objectively visible in this comic panel with {figure_text} in {motion_text} scene{object_text}. "
            f"The scene is {motion_detail}. Describe ONLY the physical elements that are definitely present: "
            f"character positions, visible objects, and panel composition. "
            f"If speech bubbles are present, ONLY mention their existence - DO NOT invent their contents unless text is clearly visible. "
            f"DO NOT make assumptions about emotions, thoughts, or narrative context. "
            f"Keep the description minimal, factual, and focused only on what can be seen."
        )
        
        system_prompt = (
            "You are a comic panel describer that ONLY states what is objectively visible. "
            "NEVER invent dialogue content, emotions, or scene details. If you see a speech bubble, "
            "only mention its presence - NEVER guess what's written inside unless the text is clearly legible. "
            "Describe only physical elements that are definitely present in the image. "
            "Do not make assumptions about what characters are thinking or feeling unless their expressions are extremely clear. "
            "Do not use interpretive language - stick to physical descriptions only. "
            "Your descriptions must be factual enough to charge money for."
        )
        
        # Try each provider in priority order
        for provider in self.priority:
            if provider == "openai" and self.keys["openai"]:
                try:
                    logger.info("Trying OpenAI for description generation")
                    return self.call_openai(system_prompt, prompt)
                except Exception as e:
                    logger.error(f"OpenAI failed: {str(e)}")
            
            elif provider == "anthropic" and self.keys["anthropic"]:
                try:
                    logger.info("Trying Anthropic for description generation")
                    return self.call_anthropic(prompt)
                except Exception as e:
                    logger.error(f"Anthropic failed: {str(e)}")
            
            elif provider == "grok" and self.keys["grok"]:
                try:
                    logger.info("Trying Grok for description generation")
                    return self.call_grok(prompt)
                except Exception as e:
                    logger.error(f"Grok failed: {str(e)}")
            
            elif provider == "deepseek" and self.keys["deepseek"]:
                try:
                    logger.info("Trying DeepSeek for description generation")
                    return self.call_deepseek(prompt)
                except Exception as e:
                    logger.error(f"DeepSeek failed: {str(e)}")
        
        # Fallback to rule-based description
        logger.info("Using rule-based description generation")
        return self._generate_rule_based_description(image_analysis, panel_num)
    
    def _generate_rule_based_description(self, image_analysis, panel_num):
        """
        Generate a rule-based description as a fallback.
        
        Args:
            image_analysis (dict): Image analysis data
            panel_num (int): Panel number
            
        Returns:
            str: Generated description
        """
        # Extract data from image analysis
        figures = len(image_analysis.get("figures", []))
        motion_type = image_analysis.get("motion", {}).get("type", "static")
        object_type = image_analysis.get("objects", {}).get("type", "none")
        
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
        if motion_type == "action":
            description += " in a scene with movement"
        else:
            description += " in a static scene"
        
        # Object description - only if definitely present
        if object_type == "sparks":
            description += " with visual effects"
        
        # End with period
        if not description.endswith("."):
            description += "."
        
        return description

# Create singleton instance
api_client = MultiProviderAPI()
