from agents.generation_agent import GenerationAgent

def test_gen():
    gen = GenerationAgent()
    
    # Mock data based on your successful test runs
    transcript = "This is a sample transcription where we discuss green circular monitors and control panels."
    descriptions = [
        "A green circular object, likely a monitor.",
        "A green screen with a circular symbol, potentially a logo.",
        "A control panel displaying data."
    ]
    
    print("--- 📄 Generating PDF ---")
    pdf_path = gen.create_pdf(transcript + " " + " ".join(descriptions), "test_summary.pdf")
    print(f"✅ PDF Created at: {pdf_path}")
    
    print("\n--- 📊 Generating PPTX ---")
    ppt_path = gen.create_ppt(transcript, descriptions, "test_report.pptx")
    print(f"✅ PPTX Created at: {ppt_path}")

if __name__ == "__main__":
    test_gen()