import os
from utils.video_processor import VideoProcessor
from agents.transcription_agent import TranscriptionAgent
from agents.vision_agent import VisionAgent
from agents.generation_agent import GenerationAgent
from agents.query_agent import QueryAgent

class VideoOrchestrator:
    def __init__(self, db_path=None):
        print("--- 🧠 Initializing AI Orchestrator ---")
        self.processor = VideoProcessor()
        self.transcriber = TranscriptionAgent(model_id="openai/whisper-tiny")
        self.vision = VisionAgent()
        self.generator = GenerationAgent()
        
        self.query_agent = QueryAgent(db_path=db_path)
        self.current_transcript = ""
        self.current_descriptions = []
        self.video_metadata = {}

    def handle_chat(self, video_id, message):
        """Bridge to the Query Agent"""
        return self.query_agent.chat(video_id, message)
    
    def process_new_video(self, video_path):
        """
        Runs the full pipeline and yields status updates for gRPC
        """
        yield "Extracting audio and frames...", 0.1
        audio_path, frames = self.processor.process_video(video_path)

        yield "Transcribing audio (OpenVINO)...", 0.3
        self.current_transcript = self.transcriber.transcribe(audio_path)

        yield "Analyzing visual content...", 0.6
        self.current_descriptions = []
        sample_size = min(5, len(frames))
        for i in range(sample_size):
            desc = self.vision.analyze_frame(frames[i], prompt="What objects or graphs are visible?")
            self.current_descriptions.append(desc)
            progress = 0.6 + (i / sample_size) * 0.3
            yield f"Analyzing frame {i+1}/{sample_size}...", progress

        yield "Finalizing report templates...", 0.9
        yield "Video processing complete!", 1.0

    def generate_report(self, report_type="pdf"):
        if report_type == "pptx":
            return self.generator.create_ppt(self.current_transcript, self.current_descriptions)
        return self.generator.create_pdf(self.current_transcript + " " + " ".join(self.current_descriptions))