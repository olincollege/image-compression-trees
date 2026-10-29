"""
Runs through an example of Huffman encoding, step by step, without saving the image.
Primarily used for debugging and demonstration.
"""

from encoding import *
from PIL import Image

input_path = "data/7x7_test.png"
output_bin_path = "data/7x7_compressed.bin"

img = Image.open(input_path).convert('RGB')
dims = img.size
pixels = img.getdata()
rgb_vals = [color for rgb in pixels for color in rgb]

# get huffman codes, encode image, and convert it to bytes
freqs = map_freqs(rgb_vals)
tree = generate_tree(freqs)
codes = generate_codes(tree)
encoding, padding = generate_encoded_string(rgb_vals, codes)
byte_list = convert_to_bytes(encoding)

# encode the metadata to bytes
metadata = generate_metadata_string(dims, padding, codes)
metadata_bytes = convert_to_bytes(metadata)

# write the metadata and encoded rgb values to the output path
#write_to_file(byte_list, metadata_bytes, output_path)