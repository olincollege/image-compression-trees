"""
Decodes a Huffman-compressed .bin file and saves the resulting image.
"""
import ast
from PIL import Image


def build_huffman_tree(huffman_dict):
    """
    Builds a Huffman tree from a dictionary of Huffman codes.

    Args:
        huffman_dict (dict): mapping of values to Huffman codes.

    Returns:
        dict: nested dictionary representing the Huffman tree.
    """
    root = {}

    for value,code in huffman_dict.items():
        current_node = root
        for bit in code:
            if bit not in current_node:
                current_node[bit] = {}
            current_node = current_node[bit]
        current_node['value'] = value
    return root


def decode_huffman(huffman_binary, huffman_dict):
    """
    Decodes a binary string using a Huffman tree.
    """
    huffman_tree = build_huffman_tree(huffman_dict)
    current_node = huffman_tree
    decoded_values = []

    for bit in huffman_binary:
        current_node = current_node[bit]
        if 'value' in current_node:
            decoded_values.append(current_node['value'])
            current_node = huffman_tree

    return decoded_values


def decode_image(input_path, output_path):
    """
    Decode a Huffman-compressed image file and save the resulting image.

    Args:
        input_path (str): path to the compressed .bin file.
        output_path (str): path where the decoded image will be saved.
    """
    with open(input_path, "rb") as file:
        image_data = file.read()

    indicator_bytes = b'\xaa\xbb\xcc'
    keys_vals_end_index = image_data.find(indicator_bytes)
    if keys_vals_end_index == -1:
        raise ValueError("Compressed image is missing its metadata separator")

    metadata = image_data[:keys_vals_end_index].lstrip(b'\x00').decode("utf-8")
    dictionary_start = metadata.find("{")
    if dictionary_start == -1:
        raise ValueError("Compressed image is missing its Huffman dictionary")

    dimensions_and_padding = metadata[:dictionary_start].split(",")
    if len(dimensions_and_padding) != 3:
        raise ValueError("Compressed image has invalid dimensions or padding metadata")

    img_width, img_height, padding = map(int, dimensions_and_padding)
    huffman_dict = ast.literal_eval(metadata[dictionary_start:])

    huffman_rgb_bytes = image_data[keys_vals_end_index + len(indicator_bytes):]
    huffman_rgb_binary = "".join(f"{byte:08b}" for byte in huffman_rgb_bytes)
    if padding:
        huffman_rgb_binary = huffman_rgb_binary[:-padding]

    pixels = decode_huffman(huffman_rgb_binary, huffman_dict)
    expected_values = img_width * img_height * 3
    if len(pixels) != expected_values:
        raise ValueError(
            f"Decoded {len(pixels)} color values; expected {expected_values}"
        )

    image = Image.new("RGB", (img_width, img_height))
    image.putdata([
        tuple(pixels[index:index + 3])
        for index in range(0, len(pixels), 3)
    ])
    image.save(output_path)
