"""Feedback processing tool for the Comic Panel MCP Server."""

import os
import json
import logging
import time
from mcp.types import ErrorCode, McpError

logger = logging.getLogger("comic-mcp-server")

async def process_feedback_tool(arguments, openai_key=None):
    """
    Process feedback from artists to improve description generation.
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    rating = arguments.get("rating")
    issue_type = arguments.get("issue_type")
    original_description = arguments.get("original_description")
    edited_description = arguments.get("edited_description")
    comments = arguments.get("comments")
    
    if not rating or not original_description or not edited_description:
        raise McpError(ErrorCode.InvalidParams, "Missing required parameters")
    
    try:
        # Store the feedback
        feedback_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        feedback_file = os.path.join(feedback_dir, f"feedback_{int(time.time())}.json")
        
        feedback_data = {
            "rating": rating,
            "issue_type": issue_type,
            "original_description": original_description,
            "edited_description": edited_description,
            "comments": comments,
            "timestamp": time.time()
        }
        
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        # Analyze the feedback to learn from it
        analysis = analyze_feedback(feedback_data)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "success": True,
                        "message": "Feedback processed successfully",
                        "analysis": analysis
                    }, indent=2)
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in process_feedback_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error processing feedback: {str(e)}")

def analyze_feedback(feedback_data):
    """
    Analyze feedback to learn from it.
    
    Args:
        feedback_data (dict): Feedback data
        
    Returns:
        dict: Analysis results
    """
    # Extract data
    rating = feedback_data.get("rating")
    issue_type = feedback_data.get("issue_type")
    original = feedback_data.get("original_description", "")
    edited = feedback_data.get("edited_description", "")
    
    # Initialize analysis
    analysis = {
        "rating": rating,
        "issue_type": issue_type,
        "changes_detected": False,
        "change_type": "none",
        "lessons": []
    }
    
    # Check if there are changes
    if original != edited:
        analysis["changes_detected"] = True
        
        # Analyze what kind of changes were made
        if len(edited) < len(original) * 0.8:
            analysis["change_type"] = "significant_reduction"
            analysis["lessons"].append("Descriptions should be more concise")
        elif len(edited) > len(original) * 1.2:
            analysis["change_type"] = "significant_addition"
            analysis["lessons"].append("Descriptions may be missing important details")
        else:
            analysis["change_type"] = "refinement"
            analysis["lessons"].append("Descriptions need minor refinements")
        
        # Check for specific issues based on issue_type
        if issue_type == "made-up-details":
            analysis["lessons"].append("Avoid making up details not present in the image")
        elif issue_type == "missed-elements":
            analysis["lessons"].append("Pay more attention to all elements in the image")
        elif issue_type == "wrong-interpretation":
            analysis["lessons"].append("Stick to objective descriptions without interpretation")
        elif issue_type == "too-verbose":
            analysis["lessons"].append("Keep descriptions more concise")
        elif issue_type == "too-brief":
            analysis["lessons"].append("Include more relevant details in descriptions")
    
    return analysis
