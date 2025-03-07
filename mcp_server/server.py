#!/usr/bin/env python3
import os
import sys
import logging
from mcp import Server, StdioServerTransport
from mcp.types import (
    ListToolsRequestSchema,
    CallToolRequestSchema,
    ErrorCode,
    McpError,
)
from .tools import (
    detect_objects_tool,
    classify_scene_tool,
    analyze_relationships_tool,
    generate_description_tool,
    analyze_panel_tool,
    verify_description_tool,
    process_feedback_tool
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("comic-mcp-server")

class ComicPanelMcpServer:
    """MCP server for comic panel analysis and description generation."""
    
    def __init__(self):
        """Initialize the MCP server with tools for comic panel analysis."""
        self.server = Server(
            {
                "name": "comic-panel-mcp-server",
                "version": "0.1.0",
            },
            {
                "capabilities": {
                    "tools": {},
                },
            }
        )
        
        # Load API keys from environment variables
        self.openai_key = os.environ.get('OPENAI_API_KEY', '')
        
        # Set up request handlers
        self._setup_tool_handlers()
        
        # Error handling
        self.server.onerror = lambda error: logger.error(f"MCP Error: {error}")
    
    def _setup_tool_handlers(self):
        """Set up handlers for MCP tools."""
        # List available tools
        self.server.setRequestHandler(ListToolsRequestSchema, self._handle_list_tools)
        
        # Call tool handler
        self.server.setRequestHandler(CallToolRequestSchema, self._handle_call_tool)
    
    async def _handle_list_tools(self, _request):
        """Handle request to list available tools."""
        return {
            "tools": [
                {
                    "name": "detect_objects",
                    "description": "Detect objects in a comic panel image",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data or path to image file"
                            },
                            "is_path": {
                                "type": "boolean",
                                "description": "Whether image_data is a file path (true) or base64 encoded image (false)",
                                "default": True
                            }
                        },
                        "required": ["image_data"]
                    }
                },
                {
                    "name": "classify_scene",
                    "description": "Classify the scene type in a comic panel",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data or path to image file"
                            },
                            "is_path": {
                                "type": "boolean",
                                "description": "Whether image_data is a file path (true) or base64 encoded image (false)",
                                "default": True
                            }
                        },
                        "required": ["image_data"]
                    }
                },
                {
                    "name": "analyze_relationships",
                    "description": "Analyze relationships between objects in a comic panel",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data or path to image file"
                            },
                            "figures": {
                                "type": "array",
                                "description": "List of detected figures with bounding boxes",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "is_path": {
                                "type": "boolean",
                                "description": "Whether image_data is a file path (true) or base64 encoded image (false)",
                                "default": True
                            }
                        },
                        "required": ["image_data", "figures"]
                    }
                },
                {
                    "name": "generate_description",
                    "description": "Generate a description for a comic panel based on analysis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "panel_num": {
                                "type": "integer",
                                "description": "Panel number",
                                "default": 1
                            },
                            "figures": {
                                "type": "array",
                                "description": "Detected figures in the panel"
                            },
                            "scene_type": {
                                "type": "string",
                                "description": "Classified scene type"
                            },
                            "attributes": {
                                "type": "array",
                                "description": "Scene attributes"
                            },
                            "relationships": {
                                "type": "array",
                                "description": "Relationships between figures"
                            }
                        },
                        "required": ["figures", "scene_type", "relationships"]
                    }
                },
                {
                    "name": "analyze_panel",
                    "description": "Complete analysis of a comic panel (all steps in one)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data or path to image file"
                            },
                            "panel_num": {
                                "type": "integer",
                                "description": "Panel number",
                                "default": 1
                            },
                            "is_path": {
                                "type": "boolean",
                                "description": "Whether image_data is a file path (true) or base64 encoded image (false)",
                                "default": True
                            }
                        },
                        "required": ["image_data"]
                    }
                },
                {
                    "name": "verify_description",
                    "description": "Verify a description to ensure it's factual and doesn't contain speculative content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description to verify"
                            }
                        },
                        "required": ["description"]
                    }
                },
                {
                    "name": "process_feedback",
                    "description": "Process feedback from artists to improve description generation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "rating": {
                                "type": "string",
                                "description": "Rating (1-5)"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Type of issue (made-up-details, missed-elements, etc.)"
                            },
                            "original_description": {
                                "type": "string",
                                "description": "Original description"
                            },
                            "edited_description": {
                                "type": "string",
                                "description": "Edited description"
                            },
                            "comments": {
                                "type": "string",
                                "description": "Additional comments"
                            }
                        },
                        "required": ["rating", "original_description", "edited_description"]
                    }
                }
            ]
        }
    
    async def _handle_call_tool(self, request):
        """Handle request to call a tool."""
        tool_name = request.params.name
        arguments = request.params.arguments
        
        logger.info(f"Tool call: {tool_name}")
        
        try:
            if tool_name == "detect_objects":
                return await detect_objects_tool(arguments, self.openai_key)
            elif tool_name == "classify_scene":
                return await classify_scene_tool(arguments, self.openai_key)
            elif tool_name == "analyze_relationships":
                return await analyze_relationships_tool(arguments, self.openai_key)
            elif tool_name == "generate_description":
                return await generate_description_tool(arguments, self.openai_key)
            elif tool_name == "analyze_panel":
                return await analyze_panel_tool(arguments, self.openai_key)
            elif tool_name == "verify_description":
                return await verify_description_tool(arguments, self.openai_key)
            elif tool_name == "process_feedback":
                return await process_feedback_tool(arguments, self.openai_key)
            else:
                raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error in tool {tool_name}: {str(e)}")
    
    async def run(self):
        """Run the MCP server."""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Comic Panel MCP server running on stdio")


async def main():
    """Main entry point for the MCP server."""
    server = ComicPanelMcpServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
