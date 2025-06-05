from PIL import Image
import sys
import os

def convert_webp_to_png(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img.save(output_path, "PNG")
        print(f"Converted '{input_path}' to '{output_path}' successfully.")
    except Exception as e:
        print(f"Error converting image: {e}")

def print_usage():
    print("Usage: python webp_to_png_converter.py input_file.webp output_file.png")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Input file '{input_file}' does not exist.")
        sys.exit(1)

    convert_webp_to_png(input_file, output_file)
