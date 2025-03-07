"""Description verification tool for the Comic Panel MCP Server."""

import logging
import re
from mcp.types import ErrorCode, McpError

logger = logging.getLogger("comic-mcp-server")

async def verify_description_tool(arguments, openai_key=None):
    """
    Verify a description to ensure it's factual and doesn't contain speculative content.
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    description = arguments.get("description")
    
    if not description:
        raise McpError(ErrorCode.InvalidParams, "Missing description parameter")
    
    try:
        # Verify the description
        verified_description = verify_description(description)
        
        # Return the verified description
        return {
            "content": [
                {
                    "type": "text",
                    "text": verified_description
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in verify_description_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error verifying description: {str(e)}")

def verify_description(description):
    """
    Verify a description to ensure it's factual and doesn't contain speculative content.
    
    Args:
        description (str): Description to verify
        
    Returns:
        str: Verified description
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
    verified_description = description
    for pattern, replacement in speculative_phrases:
        verified_description = re.sub(pattern, replacement, verified_description, flags=re.IGNORECASE)
    
    # Clean up any double spaces
    verified_description = re.sub(r'\s+', ' ', verified_description)
    
    return verified_description
