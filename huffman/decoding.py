"""
Takes in a .bin file and outputs an image
"""
import ast
from PIL import Image

input_path = "data/7x7_compressed.bin"

# open binary file
with open(input_path, "rb") as file:
    image_data = file.read()
    # print(image_data)

# print(type(image_data))

# indicator string
indicator_bytes = b'\xaa\xbb\xcc'

keys_vals_end_index = image_data.find(indicator_bytes)
metadata_keys_vals = image_data[:keys_vals_end_index]

first_comma_index = metadata_keys_vals.find(b',')
second_comma_index = metadata_keys_vals[first_comma_index+1:].find(b',')
third_comma_index = metadata_keys_vals[first_comma_index+1+second_comma_index:].find(b',')
leading_zeros_index = metadata_keys_vals.find(b'\x00')
metadata = metadata_keys_vals[leading_zeros_index+len(b'\x00'):first_comma_index+1+second_comma_index+1+third_comma_index+1]
img_width = int(metadata.split(b',')[0])
img_height = int(metadata.split(b',')[1])
padding = int(metadata.split(b',')[2])

keys_vals = metadata_keys_vals[first_comma_index+1+second_comma_index+1+third_comma_index+1:]
huffman_dict = ast.literal_eval(keys_vals.decode("utf-8"))
print(huffman_dict)

huffman_rgb_bytes = image_data[(keys_vals_end_index+len(indicator_bytes)):]

huffman_rgb_binary = "".join(f"{byte:08b}" for byte in huffman_rgb_bytes)
huffman_rgb_binary = huffman_rgb_binary[:len(huffman_rgb_binary)-padding]

# tree that represents the huffman codes
def build_huffman_tree(huffman_dict):
    """
    Builds a Huffman tree from a dictionary of Huffman codes.

    Args:
        
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

pixels = decode_huffman(huffman_rgb_binary, huffman_dict)
image = Image.new("RGB", (img_width, img_height))
image_pixels = image.load()

for x in range(img_width):
    for y in range(img_height):
        pixel_index = y*img_width + x
        image_pixels[x,y] = (pixels[pixel_index*3], pixels[pixel_index*3+1], pixels[pixel_index*3+2])

image.save("data/7x7_decompressed.png")
image.show()