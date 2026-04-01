from pathlib import Path
from optimum.intel.openvino import OVModelForSpeechSeq2Seq
from transformers import AutoProcessor, pipeline

class TranscriptionAgent:
    def __init__(self, model_path=None):
        if model_path is None:
            current_file = Path(__file__).resolve()
            model_path = current_file.parent.parent / "models" / "whisper"

        print(f"--- 🎙️ Loading Transcription Agent from: {model_path} ---")
        
        # Check if we need to export (look for the encoder xml)
        encoder_xml = model_path / "openvino_encoder_model.xml"
        should_export = not encoder_xml.exists()

        if should_export:
            print("📦 One-time export: Converting Whisper to OpenVINO IR...")
        
        self.model = OVModelForSpeechSeq2Seq.from_pretrained(
            str(model_path), 
            device="CPU",
            export=should_export,
            local_files_only=True,
            compile=True
        )
        self.processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            chunk_length_s=30,
            device="cpu",
        )

    def transcribe(self, audio_path):
        result = self.pipe(audio_path)
        return result["text"]