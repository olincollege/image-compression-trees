from PIL import Image
import json

"""
"""
def encode_image(input_path, output_path):
    img = Image.open(input_path).convert('RGB')
    dims = img.size
    pixels = img.getdata()
    rgb_vals = [color for rgb in pixels for color in rgb]
    
    freqs = map_freqs(rgb_vals)
    tree = generate_tree(freqs)
    codes = generate_codes(tree)
    encoding, padding = generate_encoded_string(rgb_vals, codes)
    byte_list = convert_to_bytes(encoding)

    metadata = generate_metadata_string(dims, padding, codes)
    metadata_bytes = convert_to_bytes(metadata)

    write_to_file(byte_list, metadata_bytes, output_path)


"""
"""
def map_freqs(color_list):
    freqs = {val: 0 for val in set(color_list)}

    for val in color_list:
        freqs[val] += 1

    return freqs


"""
"""
def generate_tree(freqs):
    tree = list(freqs.keys())
    while (len(tree) > 1):
        tree.sort(key=lambda val: freqs[val])
        right = tree.pop(0)
        left = tree.pop(0)
        branch = (left, right)
        freqs[branch] = freqs[left] + freqs[right]
        del freqs[left], freqs[right]
        tree.append(branch)

    return tree[0]


"""
"""
def generate_codes(tree):
    codes = {}
    for i in range(len(tree)):
        if isinstance(tree[i], int):
            codes |= {tree[i]: f"{i}"}
        else:
            subcodes = generate_codes(tree[i])
            for key in subcodes.keys():
                subcodes[key] = f"{i}{subcodes[key]}"
                codes |= subcodes

    return codes


"""
"""
def generate_encoded_string(values, codes):
    string = ""
    for value in values:
        string += codes[value]
    padding = 8 - (len(string)%8)
    string += '0'*padding
    return string, padding


"""
"""
def generate_metadata_string(dims, padding, codes):
    codes_str = ""
    for key in codes.keys():
        codes_str += f",{key},{codes[key]}"
    
    string = f"{dims[0]},{dims[1]},{padding},{codes}"
    b_string = ''.join(format(ord(char), '08b') for char in string)

    padding = 8-(len(b_string)%8)
    b_string = '0'*padding + b_string

    return b_string


"""
"""
def convert_to_bytes(string):
    if len(string)%8 != 0:
        raise ValueError("String not padded correctly")
    
    byte_list = []
    for i in range(0, len(string), 8):
        byte = string[i:i+8]
        byte_list.append(int(byte, 2))

    return bytes(byte_list)


"""
"""
def write_to_file(byte_list, metadata, path):
    separation_code = b'\xAA\xBB\xCC'
    with open(path, 'wb') as f:
        f.write(metadata)
        f.write(separation_code)
        f.write(byte_list)