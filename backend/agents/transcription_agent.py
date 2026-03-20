from optimum.intel.openvino import OVModelForSpeechSeq2Seq
from transformers import AutoProcessor, pipeline

class TranscriptionAgent:
    def __init__(self, model_id="openai/whisper-base"):
        # This will download and convert the model to OpenVINO format locally
        self.model = OVModelForSpeechSeq2Seq.from_pretrained(
            model_id, 
            export=True, 
            device="CPU" # OpenVINO targets the CPU for local inference
        )
        self.processor = AutoProcessor.from_pretrained(model_id)
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