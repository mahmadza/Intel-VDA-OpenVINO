import openvino_genai as ov_genai
import sqlite3
import os
from agents.generation_agent import GenerationAgent

class QueryAgent:
    def __init__(self, model_path=None, db_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "llm")
        
        print(f"--- 🤖 Loading Query Agent from: {model_path} ---")
        self.pipe = ov_genai.LLMPipeline(model_path, "CPU")
        self.db_path = db_path
        self.generator = GenerationAgent()

    def _get_video_context(self, video_id):
        if not self.db_path or not os.path.exists(self.db_path):
            return ""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Get the main transcription/summary
            cursor.execute("SELECT transcription_text, summary FROM analysis_results WHERE video_id = ?", (video_id,))
            main_data = cursor.fetchone()
            
            # 2. Get the visual segments (frames analyzed)
            cursor.execute("SELECT content FROM video_segments WHERE video_id = ?", (video_id,))
            segments = cursor.fetchall()
            conn.close()
            
            context_parts = []
            if main_data:
                context_parts.append(f"TRANSCRIPT: {main_data[0]}")
                context_parts.append(f"SUMMARY: {main_data[1]}")
            
            if segments:
                visuals = "\n".join([f"- {s[0]}" for s in segments])
                context_parts.append(f"VISUAL OBSERVATIONS:\n{visuals}")

            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"❌ DB Query Error: {e}")
            return ""
        
    def _get_chat_history(self, video_id, limit=5):
        """Fetches the last N messages to provide conversation context."""
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
            
            # Reverse messages so they are in chronological order
            history = []
            for role, content in reversed(rows):
                prefix = "User" if role == "user" else "Assistant"
                history.append(f"{prefix}: {content}")
            return "\n".join(history)
        except Exception as e:
            print(f"❌ Chat History Error: {e}")
            return ""

    def chat(self, video_id, user_query):
        context = self._get_video_context(video_id)
        chat_history = self._get_chat_history(video_id)

        norm_query = user_query.strip().upper()

        # If the user provides a direct format after we asked
        if norm_query in ["PDF", "PPT", "POWERPOINT"]:
            format_type = "pdf" if norm_query == "PDF" else "pptx"
            report_text = f"ANALYSIS:\n{context}\n\nCHAT HISTORY:\n{chat_history}"
            
            if format_type == "pdf":
                path = self.generator.create_pdf(report_text)
            else:
                path = self.generator.create_ppt(context, chat_history)
            return f"SUCCESS_FILE: {path}"

        # General request check
        if "REPORT" in norm_query or "GENERATE" in norm_query:
            if "PDF" in norm_query:
                path = self.generator.create_pdf(f"ANALYSIS:\n{context}\n\nCHAT HISTORY:\n{chat_history}")
                return f"SUCCESS_FILE: {path}"
            elif "PPT" in norm_query or "POWERPOINT" in norm_query:
                path = self.generator.create_ppt(context, chat_history)
                return f"SUCCESS_FILE: {path}"
            else:
                return "I can certainly generate a report for you. Would you prefer a PDF summary or a PowerPoint presentation?"
        
        # Ambiguity check
        check_prompt = f"""<|system|>
        Analyze the user's query. Is it specific enough to answer using the context? 
        If it is vague (e.g. "What is that?", "Tell me more"), output "AMBIGUOUS".
        Otherwise, output "CLEAR".
        QUERY: {user_query}
        <|end|>
        <|assistant|>"""
        
        decision = self.pipe.generate(check_prompt, max_new_tokens=10).strip()

        if "AMBIGUOUS" in decision.upper():
            return "I'm not sure which part of the video you're referring to. Could you clarify if you mean the audio discussion or one of the visual objects I found?"
        
        prompt = f"""<|system|>
        You are a Technical Video Analyst. Your ONLY job is to answer questions using the provided ANALYSIS NOTES.
        
        ### STRICT RULES:
        1. Only use the provided ANALYSIS NOTES. 
        2. If information is not in the notes, state: "That information is not present in the video analysis."
        3. Do NOT describe your general AI capabilities or list features.
        4. Be concise and clinical. No "meandering" or introductory fluff.
        5. If the user asks about "you" or "your capabilities", redirect them to ask about the video content.

        ### ANALYSIS NOTES:
        {context}

        ### RECENT CHAT HISTORY (FOR CONTEXT):
        {chat_history}
        <|end|>
        <|user|>
        {user_query}<|end|>
        <|assistant|>
        """
        # Use a low max_new_tokens to force conciseness
        response = self.pipe.generate(prompt, max_new_tokens=200).strip()
        
        # Clean up any residual hallucinated prefixes
        return response.split("Assistant:")[-1].strip()