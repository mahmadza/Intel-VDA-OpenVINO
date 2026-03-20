from optimum.intel.openvino import OVModelForVisualCausalLM
from transformers import AutoProcessor
from PIL import Image
import torch

class VisionAgent:
    def __init__(self, model_id="HuggingFaceTB/SmolVLM2-256M-Instruct"):
        print(f"Loading Native OpenVINO Vision Model: {model_id}...")
        
        # SmolVLM2 is natively supported, so 'export=True' works perfectly here
        self.model = OVModelForVisualCausalLM.from_pretrained(
            model_id,
            export=True,
            device="CPU",
            trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(model_id)

    def analyze_frame(self, image_path, prompt="Describe this image."):
        image = Image.open(image_path).convert("RGB")
        
        # SmolVLM2 uses a specific prompt format (User: <prompt>\nAssistant:)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Prepare inputs using the processor's chat template
        input_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=input_text, images=[image], return_tensors="pt")
        
        # Generate answer
        output = self.model.generate(**inputs, max_new_tokens=150)
        
        # Decode and clean up (remove the prompt from the output)
        full_text = self.processor.decode(output[0], skip_special_tokens=True)
        answer = full_text.split("Assistant:")[-1].strip()
        
        return answer