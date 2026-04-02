import os
from PIL import Image

def generate_icons():
    # scripts/ から見て ../assets/logo.png を探す
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "assets", "logo.png")
    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} not found.")
        return

    img = Image.open(logo_path)
    
    # logo.ico を assets/ に保存
    ico_path = os.path.join(base_dir, "assets", "logo.ico")
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Successfully generated {ico_path}")

if __name__ == "__main__":
    generate_icons()
