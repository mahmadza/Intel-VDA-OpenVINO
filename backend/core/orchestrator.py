from utils.video_processor import VideoProcessor
from agents.transcription_agent import TranscriptionAgent
from agents.vision_agent import VisionAgent
from agents.generation_agent import GenerationAgent
from agents.query_agent import QueryAgent

class VideoOrchestrator:
    def __init__(self, db_path=None):
        print("--- 🧠 Initializing AI Orchestrator ---")
        self.processor = VideoProcessor()
        self.transcriber = TranscriptionAgent()
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
        yield "STEP 1/4: Extracting audio and keyframes...", 0.1
        audio_path, frames = self.processor.process_video(video_path)

        yield "STEP 2/4: Transcribing speech (OpenVINO)...", 0.3
        self.current_transcript = self.transcriber.transcribe(audio_path)
        
        yield "STEP 3/4: Analyzing visual intelligence...", 0.5
        self.current_descriptions = []
        
        sample_size = min(12, len(frames)) 
        
        for i in range(sample_size):
            simple_prompt = "Describe the main objects and actions in this image concisely."
            desc = self.vision.analyze_frame(frames[i], prompt=simple_prompt)
            
            self.current_descriptions.append(f"Frame {i}: {desc}")
            
            progress = 0.5 + (i / sample_size) * 0.4 
            yield f"STEP 3/4: Processing visual frame {i+1} of {sample_size}...", progress

        yield "Analysis Complete!", 1.0

    def generate_report(self, report_type="pdf"):
        if report_type == "pptx":
            return self.generator.create_ppt(self.current_transcript, self.current_descriptions)
        return self.generator.create_pdf(self.current_transcript + " " + " ".join(self.current_descriptions))