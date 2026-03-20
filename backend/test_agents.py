import os
from utils.video_processor import VideoProcessor
from agents.transcription_agent import TranscriptionAgent
from agents.vision_agent import VisionAgent

def main():
    video_path = "sample.mp4"
    temp_dir = "temp_output"
    
    if not os.path.exists(video_path):
        print(f"❌ Error: {video_path} not found. Please add a sample video.")
        return

    print("--- 🛠️ Step 1: Pre-processing Video ---")
    vp = VideoProcessor()
    audio_path, frames = vp.process_video(video_path, output_dir=temp_dir)
    print(f"✅ Audio extracted to: {audio_path}")
    print(f"✅ {len(frames)} frames extracted.")

    print("\n--- 🧠 Step 2: Initializing Transcription Agent (OpenVINO) ---")
    # This will take a moment the first time (model download/conversion)
    agent = TranscriptionAgent(model_id="openai/whisper-tiny") # Using 'tiny' for faster testing
    
    print("\n--- 📝 Step 3: Transcribing ---")
    transcript = agent.transcribe(audio_path)
    
    print("\n--- 🎯 Result ---")
    print(transcript)

    print("\n--- 👁️ Step 4: Initializing Vision Agent (OpenVINO) ---")
    v_agent = VisionAgent()

    print("\n--- 📊 Step 5: Analyzing Key Frames ---")
    for frame in frames[:3]:
        print(f"\nAnalyzing: {frame}")
        # Specific query from the Intel
        desc = v_agent.analyze_frame(frame, prompt="Are there any graphs or objects? Describe them.")
        print(f"Model says: {desc}")

if __name__ == "__main__":
    main()