# backend/agents/generation_mcp_server.py
from mcp.server.fastmcp import FastMCP
from generation_agent import GenerationAgent

mcp = FastMCP("Intel VDA Generation Server")
generator = GenerationAgent()

@mcp.tool()
def generate_pdf_report(content: str, output_path: str = "video_summary.pdf") -> str:
    """Generates a PDF report summarizing the video analysis."""
    path = generator.create_pdf(content, output_path)
    return f"SUCCESS_FILE: {path}"

@mcp.tool()
def generate_ppt_report(transcript: str, chat_history: str, output_path: str = "video_report.pptx") -> str:
    """Generates a PowerPoint presentation from the video transcript and chat."""
    path = generator.create_ppt(transcript, chat_history, output_path)
    return f"SUCCESS_FILE: {path}"

if __name__ == "__main__":
    print("🚀 Starting Intel VDA Generation MCP Server on port 8000 (SSE)...")
    mcp.run(transport="sse")