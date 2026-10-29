"""
Runs functions from encoding and decoding files to test encoding and decoding images
with Huffman codes.
"""

from encoding import encode_image
from decoding import decode_image
from image_generation import generate_image
import os
import time

def main():
    """
    Writes data to a csv file for color and size benchmarks.
    """
    with open('data/huffman_benchmarks.csv', 'w') as f:
        f.write('Pixels,Colors,BeforeSize,BinSize,AfterSize,Runtime')
    print('COLOR SWEEP')
    for c in range(1000):
        print(f'{c+1}/1000')
        data = benchmark(100, c+1, 10)
        with open('data/huffman_benchmarks.csv', 'a') as f:
            f.write('\n' + ','.join(map(str, data)))
    print('SIZE SWEEP')
    for s in range(1000):
        print(f'{s+1}/1000')
        data = benchmark(s+3, 5, 10)
        with open('data/huffman_benchmarks.csv', 'a') as f:
                    f.write('\n' + ','.join(map(str, data)))


def benchmark(size, colors, repetitions):
    """
    Finds the runtime and compression ratio for the compression of an image at
    a particular size and with a particular number of colors. It repeats a trial
    by a specified number of times to get a more reliable average value.

    Args:
        size (int): the length of one of the square sides of the image to compress.

        colors (int): the total number of colors present in the image to compress.

        repetitions (int): the number of repetitions of a trial, for the average count.
    
    Returns:
        list: a list of numerical values representing information about the data in a particular
        order. The order is as follows:
        The total number of pixels in the image (int),
        The number of colors in the image (int),
        the size in bytes of the image to be compressed (double),
        the size in bytes of the binary file of compressed data (double),
        the size in bytes of the final encoded and decoded image (double),
        the runtime of the process (double).

    """
    # define paths
    input_path = "data/test.jpeg"
    output_bin_path = "data/test.bin"
    output_image_path = "data/test_decompressed.jpeg"

    # initialize tracker variables
    runtime = 0
    initial_size = 0
    compressed_bin_size = 0
    compressed_image_size = 0

    for _ in range(repetitions):
        # generate image
        generate_image(size, colors, input_path)

        # run encoding/decoding
        start_time = time.time()
        encode_image(input_path, output_bin_path)
        decode_image(output_bin_path, output_image_path)

        # add to trackers cumulatively
        runtime += time.time() - start_time
        initial_size += os.path.getsize(input_path)
        compressed_bin_size += os.path.getsize(output_bin_path)
        compressed_image_size += os.path.getsize(output_image_path)

    # divide by repetitions to get averages
    runtime /= repetitions
    initial_size /= repetitions
    compressed_bin_size /= repetitions
    compressed_image_size /= repetitions

    # compare ratios and runtime
    print(initial_size/compressed_bin_size)
    print(initial_size/compressed_image_size)
    print()

    return [size*size, colors, initial_size, compressed_bin_size, compressed_image_size, runtime]


if __name__ == "__main__":
    main()