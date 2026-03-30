from optimum.intel.openvino import OVModelForVisualCausalLM
from transformers import AutoProcessor
from PIL import Image
import torch

class VisionAgent:
    def __init__(self, model_id="HuggingFaceTB/SmolVLM2-256M-Instruct"):
        print(f"Loading Native OpenVINO Vision Model: {model_id}...")
        
        self.model = OVModelForVisualCausalLM.from_pretrained(
            model_id,
            export=True,
            device="CPU",
        )
        self.processor = AutoProcessor.from_pretrained(model_id)

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