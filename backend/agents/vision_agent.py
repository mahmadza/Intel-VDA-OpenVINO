from optimum.intel.openvino import OVModelForVisualCausalLM
from transformers import AutoProcessor
from PIL import Image
from pathlib import Path

class VisionAgent:
    def __init__(self, model_path=None):
        if model_path is None:
            current_file = Path(__file__).resolve()
            model_path = current_file.parent.parent / "models" / "vision"

        print(f"--- 👁️ Loading Vision Agent from: {model_path} ---")
        
        model_xml = model_path / "openvino_model.xml"
        should_export = not model_xml.exists()

        if should_export:
            print("📦 One-time export: Converting SmolVLM2 to OpenVINO IR...")

        self.model = OVModelForVisualCausalLM.from_pretrained(
            str(model_path),
            device="CPU",
            export=should_export, # 👈 True only if .xml is missing
            local_files_only=True,
            compile=True
        )
        self.processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)

    def analyze_frame(self, image_path, prompt="Describe this image."):
        image = Image.open(image_path).convert("RGB")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        input_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
        output = self.model.generate(**inputs, max_new_tokens=150)
        full_text = self.processor.decode(output[0], skip_special_tokens=True)
        answer = full_text.split("Assistant:")[-1].strip()
        
        return answer