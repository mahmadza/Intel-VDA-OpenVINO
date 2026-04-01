# backend/agents/query_agent.py
import openvino_genai as ov_genai
import sqlite3
import os
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

class QueryAgent:
    def __init__(self, model_path=None, db_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "llm")
        
        print(f"--- 🤖 Loading Router & Query Agent from: {model_path} ---")
        self.pipe = ov_genai.LLMPipeline(model_path, "CPU")
        self.db_path = db_path

    def _get_video_context(self, video_id):
        if not self.db_path or not os.path.exists(self.db_path):
            return ""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT transcription_text, summary FROM analysis_results WHERE video_id = ?", (video_id,))
            main_data = cursor.fetchone()
            
            cursor.execute("SELECT content FROM video_segments WHERE video_id = ?", (video_id,))
            segments = cursor.fetchall()
            conn.close()
            
            context_parts = []
            
            # 🔥 FIX: Use extremely explicit labels so the LLM knows this is the audio/dialogue
            if main_data:
                transcript = main_data[0] if main_data[0] and main_data[0].strip() else "[No speech detected in video]"
                context_parts.append(f"AUDIO TRANSCRIPT (What was spoken in the video):\n{transcript}")
            
            if segments:
                visuals = "\n".join([f"- {s[0]}" for s in segments])
                context_parts.append(f"VISUAL OBSERVATIONS:\n{visuals}")

            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"❌ DB Error: {e}")
            return ""
        
    def _get_chat_history(self, video_id, limit=5):
        if not self.db_path or not os.path.exists(self.db_path):
            return ""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE video_id = ? ORDER BY id DESC LIMIT ?", 
                (video_id, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for role, content in reversed(rows):
                prefix = "User" if role == "user" else "Assistant"
                history.append(f"{prefix}: {content}")
            return "\n".join(history)
        except Exception as e:
            return ""

    async def _call_mcp_tool(self, tool_name, arguments):
        """Standardized MCP Client connecting over SSE to avoid gRPC fork clashes."""
        url = "http://127.0.0.1:8000/sse" # <-- Update to 8000
        try:
            async with sse_client(url) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result.content[0].text
        except Exception as e:
            print(f"❌ MCP Connection Error: {e}")
            return f"System Error: MCP Server unreachable. Is the generation_mcp_server.py running? ({e})"

    def chat(self, video_id, user_query):
        context = self._get_video_context(video_id)
        chat_history = self._get_chat_history(video_id)

        # DEBUG: Let's see exactly what the LLM is reading
        print(f"🔍 DEBUG: Context length loaded: {len(context)} chars")
        if len(context) < 10:
            print("⚠️ WARNING: Context is virtually empty! Did the Vision/Audio agents extract data?")
            context = "[NO VISUAL OR AUDIO DATA FOUND FOR THIS VIDEO]"

        # 1. Semantic Router (Intent Classification)
        router_prompt = f"""<|system|>
        You are an AI router. Classify the user's query into ONE of these exact categories:
        - GENERATE_PDF: User asked for a PDF report or summary document.
        - GENERATE_PPT: User asked for a PowerPoint or PPT presentation.
        - AMBIGUOUS: The request is extremely vague and completely lacks a subject (e.g., "what is that?", "tell me more about it").
        - RAG_QUERY: User is asking about the video's objects, audio, what was spoken, or asking for a summary of the video/discussion.
        
        Reply ONLY with the exact category name.
        <|end|>
        <|user|>
        {user_query}<|end|>
        <|assistant|>"""
        
        intent = self.pipe.generate(router_prompt, max_new_tokens=10).strip().upper()
        print(f"🧭 Router classified intent as: {intent}")

        # 2. Agentic Execution
        if "GENERATE_PDF" in intent:
            report_text = f"ANALYSIS:\n{context}\n\nCHAT HISTORY:\n{chat_history}"
            return asyncio.run(self._call_mcp_tool("generate_pdf_report", {"content": report_text}))

        elif "GENERATE_PPT" in intent:
            return asyncio.run(self._call_mcp_tool("generate_ppt_report", {"transcript": context, "chat_history": chat_history}))

        elif "AMBIGUOUS" in intent:
            return "I'm not exactly sure what you're referring to. Could you provide a bit more detail about what you're looking for?"

        # 3. Fallback to Standard RAG with HARDENED PROMPT
        prompt = f"""<|system|>
        You are an AI Video Analyst. Answer the user's question using ONLY the provided ANALYSIS NOTES. 
        The notes contain the audio TRANSCRIPT and VISUAL OBSERVATIONS from the video.
        If the user asks about objects, list what you see in the visual observations.
        If the user asks about audio or dialogue, summarize the transcript.

        ANALYSIS NOTES:
        {context}
        <|end|>
        <|user|>
        Previous chat for context:
        {chat_history}
        
        Current question: {user_query}<|end|>
        <|assistant|>
        """
        response = self.pipe.generate(prompt, max_new_tokens=200).strip()
        return response.split("Assistant:")[-1].strip()