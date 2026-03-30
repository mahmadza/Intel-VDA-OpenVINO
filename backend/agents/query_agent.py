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
        print(f"--- 📂 DB Path configured as: {db_path}")
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

    def chat(self, video_id, user_query):
        context = self._get_video_context(video_id)
        
        if not context:
            return "I have not finished analyzing this video yet. Please wait a moment."

        prompt = f"""<|system|>
    You are the Intel VDA Video Expert. You have just watched a video and taken the following notes. 
    Answer the user's question using ONLY these notes. If the answer isn't in the notes, say you don't see that specific detail.
    NOTES:
    {context}
    <|end|>
    <|user|>
    {user_query}<|end|>
    <|assistant|>
    """
        return self.pipe.generate(prompt, max_new_tokens=300)