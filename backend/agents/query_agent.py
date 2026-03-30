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
        """
        Internal 'Resource' Tool (MCP-style): Fetches context from SQLite.
        """
        if not self.db_path or not os.path.exists(self.db_path):
            return "No database found. Cannot retrieve video context."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Fetch both transcription and visual descriptions
            # Note: We query by the video_id passed from the frontend
            cursor.execute("SELECT content FROM video_segments WHERE video_id = ?", (video_id,))
            rows = cursor.fetchall()
            conn.close()
            
            context = "\n".join([row[0] for row in rows])
            print(f"--- 🧠 AI CONTEXT FETCH (ID: {video_id}) ---")
            if context:
                print(f"FOUND: {context[:200]}...") # Print first 200 chars
            else:
                print("⚠️ EMPTY CONTEXT - Check DB path and Video ID!")
            return context
        except Exception as e:
            print(f"❌ DB Query Error: {e}")
            return ""

    def chat(self, video_id, user_query):
        context = self._get_video_context(video_id)
        
        if not context:
            return "I'm sorry, I don't have the analysis data for this video in my database yet."

        prompt = f"""<|system|>
        You are the Intel VDA Intelligence Assistant.
        You are given the following text analysis of a video. 
        Use this text to answer the user. Do NOT mention you are an AI or that you cannot watch videos.
        CONTEXT:
        {context}
        <|end|>
        <|user|>
        {user_query}<|end|>
        <|assistant|>
        """
        return self.pipe.generate(prompt, max_new_tokens=300)