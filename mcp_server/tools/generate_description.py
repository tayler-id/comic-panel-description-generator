"""Description generation tool for the Comic Panel MCP Server."""

import logging
from mcp.types import ErrorCode, McpError
from ..utils.api_utils import api_client

logger = logging.getLogger("comic-mcp-server")

async def generate_description_tool(arguments, openai_key=None):
    """
    Generate a description for a comic panel based on analysis.
    
    Args:
        arguments (dict): Tool arguments
        openai_key (str, optional): OpenAI API key
        
    Returns:
        dict: Tool response
        
    Raises:
        McpError: If an error occurs
    """
    panel_num = arguments.get("panel_num", 1)
    figures = arguments.get("figures", [])
    scene_type = arguments.get("scene_type", "unknown")
    scene_attributes = arguments.get("attributes", [])
    relationships = arguments.get("relationships", [])
    
    if not figures:
        raise McpError(ErrorCode.InvalidParams, "Missing figures parameter")
    
    try:
        # Prepare image analysis data
        image_analysis = {
            "figures": figures,
            "motion": {"type": scene_type},
            "objects": {"type": "none"},  # Default
            "relationships": relationships
        }
        
        # Generate description using the API client
        if openai_key and not api_client.keys["openai"]:
            api_client.keys["openai"] = openai_key
        
        description = api_client.generate_description(image_analysis, panel_num)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": description
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error in generate_description_tool: {str(e)}")
        raise McpError(ErrorCode.InternalError, f"Error generating description: {str(e)}")

def get_figure_desc(figures, fig_id):
    """
    Get a description of a figure by its ID.
    
    Args:
        figures (list): List of figures
        fig_id (int): Figure ID
        
    Returns:
        str: Figure description
    """
    for fig in figures:
        if fig.get("id", -1) == fig_id:
            return fig.get("description", f"Figure {fig_id}")
    return f"Figure {fig_id}"

def generate_rule_based_description(panel_num, figures, scene_type, scene_attributes, relationships):
    """
    Generate a rule-based description as a fallback.
    
    Args:
        panel_num (int): Panel number
        figures (list): List of figures
        scene_type (str): Scene type
        scene_attributes (list): Scene attributes
        relationships (list): Relationships between figures
        
    Returns:
        str: Generated description
    """
    # Start with panel number
    description = f"Panel {panel_num}: "
    
    # Add figure count and types
    figure_count = len(figures)
    if figure_count > 0:
        description += f"{figure_count} character{'s' if figure_count > 1 else ''}"
        
        # Add scene type
        if scene_type:
            description += f" in a {scene_type} scene"
        
        # Add scene attributes
        if scene_attributes:
            attributes_str = ", ".join([attr for attr in scene_attributes if attr])
            if attributes_str:
                description += f" with {attributes_str} qualities"
        
        # Add relationship information if available
        if relationships:
            # Find the most significant relationship
            if len(relationships) > 0:
                rel = relationships[0]
                fig1_id = rel.get("figure1_id", 0)
                fig2_id = rel.get("figure2_id", 1)
                rel_type = rel.get("type", "")
                
                if rel_type:
                    description += f". {get_figure_desc(figures, fig1_id)} is {rel_type} {get_figure_desc(figures, fig2_id)}"
    else:
        # No figures detected
        description += f"A scene with no visible characters"
        
        # Add scene type
        if scene_type:
            description += f", {scene_type} in nature"
    
    # End with a period if needed
    if not description.endswith("."):
        description += "."
    
    return description
