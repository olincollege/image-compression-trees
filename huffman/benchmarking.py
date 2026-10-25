"""
Runs functions from encoding and decoding files to test encoding and decoding images
with Huffman codes.
"""

from encoding import encode_image
from image_generation import generate_image
import os
import time

input_path = "data/1000x1000_100.png"
output_path = "data/1000x1000_100_compressed.bin"

repetitions = 1
runtime = 0
for _ in range(repetitions):
    start_time = time.time()
    encode_image(input_path, output_path)
    runtime += time.time() - start_time
runtime /= repetitions

initial_size = os.path.getsize(input_path)
compressed_size = os.path.getsize(output_path)
ratio = initial_size/compressed_size
print('Compression ratio:', ratio)
print('Runtime:', runtime, 's')