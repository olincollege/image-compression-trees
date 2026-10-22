"""
Runs functions from encoding and decoding files to test encoding and decoding images
with Huffman codes.
"""

from encoding import encode_image


input_path = "data/7x7_test.png"
output_path = "data/7x7_compressed.bin"
encode_image(input_path, output_path)