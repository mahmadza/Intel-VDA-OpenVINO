import openvino_genai as ov_genai
import sqlite3
import os

class QueryAgent:
    def __init__(self, model_path="models/phi3-mini-int4-ov", db_path=None):
        """
        Initializes the local LLM via OpenVINO.
        db_path: Path to the SQLite DB managed by Tauri/Rust.
        """
        print(f"--- 🤖 Loading Query Agent ---")
        print(f"--- This may take a while ---")
        self.pipe = ov_genai.LLMPipeline(model_path, "CPU")
        self.db_path = db_path

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
    You are the Intel Video Intelligence Expert. Use the Analysis Notes and Chat History to answer.
    ### ANALYSIS NOTES:
    {context}

    ### RECENT CHAT HISTORY:
    {chat_history}
    <|end|>
    <|user|>
    {user_query}<|end|>
    <|assistant|>
    """
        return self.pipe.generate(prompt, max_new_tokens=400).strip()