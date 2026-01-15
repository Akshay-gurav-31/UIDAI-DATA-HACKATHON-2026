import cairosvg
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SVG_PATH = os.path.join(BASE_DIR, "final_submission", "report_pages", "High-Level System Architecture.svg")
PNG_PATH = os.path.join(BASE_DIR, "final_submission", "images", "system_architecture.png")

def convert_architecture_diagram():
    if not os.path.exists(SVG_PATH):
        print(f"Error: SVG not found at {SVG_PATH}")
        # Create a dummy PNG if SVG is missing to prevent report failure, 
        # but in this case we assume user provided it.
        return

    print(f"Converting SVG to PNG...")
    try:
        cairosvg.svg2png(url=SVG_PATH, write_to=PNG_PATH, scale=2.0) # 2x scale for quality
        print(f"Success: Saved architecture diagram to {PNG_PATH}")
    except Exception as e:
        print(f"Conversion failed: {e}")
        # Fallback to verify if file exists anyway or let user know

if __name__ == "__main__":
    convert_architecture_diagram()
