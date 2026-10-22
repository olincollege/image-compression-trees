"""
Contains functions to encode and compress an image file using Huffman codes.
"""

from PIL import Image


def encode_image(input_path, output_path):
    """
    Uses Huffman coding to compress an image to a bin file, storing data in the following order:
    leading zeros,width,height,padding,key1,val1,key2,val2,...,keyn,valn\xAA\xBB\xCCrgbrgbrgbrgb...
    where the padding is the number of extra zeros on the end and the keys/vals are the Huffman code.

    Args:
        input_path (str): path to image to be compressed, must be image file.

        output_path (str): path at which to save the compressed output file, should be bin file.
    """
    # process image from path, get its size, and flatten the list of tuples of rgb values
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
    write_to_file(byte_list, metadata_bytes, output_path)


def map_freqs(color_list):
    """
    Determine the frequencies of each pixel intensity value as a dictionary in which the value
    is mapped to the mumber of times it occurs.

    Args:
        color_list (list): list of pixel intensity values (ints), including r, g, and b values.

    Returns:
        dict: dictionary where pixel intensity values (ints) are mapped to the number of times
        they are used (ints).
    """
    freqs = {val: 0 for val in set(color_list)}

    for val in color_list:
        freqs[val] += 1

    return freqs


def generate_tree(freqs):
    """
    Build a Huffman tree from frequencies represented by a tuple of tuples. Each tuple has two
    items, representing the two children of a binary tree. The left child is first, and the right
    child is second. An element can be an integer value (leaf), or another tuple (subtree).

    Args:
        freqs (dict): dictionary where pixel intensity values (ints) are mapped to the number of
        times they are used (ints).
    
    Returns:
        tuple: 2-element tuple representing a tree, where each value is a leaf or a subtree.
    """
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


def generate_codes(tree):
    """
    Makes a dictionary of Huffman codes by recursively searching deeper into a Huffman tree.

    Args:
        tree (tuple): 2-element tuple representing a tree, where each value is a leaf or subtree.
    
    Returns:
        dict: Dictionary in which each unique pixel intensity value (int) is mapped to a binary
        Huffman code (str).
    """
    codes = {}
    for i in range(len(tree)):
        if isinstance(tree[i], int):
            # if the element is an integer (leaf), add it to the tree
            codes[tree[i]] = f"{i}"
        else:
            # if the element is a tuple (subtree), recurse deeper and prefix with 0s/1s.
            subcodes = generate_codes(tree[i])
            for key in subcodes.keys():
                subcodes[key] = f"{i}{subcodes[key]}"
            codes |= subcodes

    return codes


def generate_encoded_string(values, codes):
    """
    Convert the list of pixel intensity values to a string containing their corresponding Huffman
    codes. Also pad the string with 0s on the end for byte conversion.

    Args:
        values (list): list of pixel intensity values (int) of pixels in image.

        codes (dict): Dictionary in which each unique pixel intensity value (int) is mapped to a
        binary Huffman code (str).
    
    Returns:
        str: binary huffman codes of each pixel intensity value, in the order they're put in.

        int: number of 0s used to pad the encoded bit string at the end.
    """
    string = ""
    for value in values:
        string += codes[value]
    padding = 8 - (len(string)%8)
    string += '0'*padding
    return string, padding


def generate_metadata_string(dims, padding, codes):
    """
    Takes in all necessary metadata for reconstruction and converts to a bit string.

    Args:
        dims (tuple): 2-element tuple with the height and width of the image, in pixels.

        padding (int): number of 0s used to pad the encoded bit string at the end.

        codes (dict): Dictionary in which each unique pixel intensity value (int) is mapped to a
        binary Huffman code (str).
    
    Returns:
        str: bit string containing metadata about the encoded image.
    """
    # convert the codes dictionary into a comma-separated list of keys and values
    codes_str = ""
    for key in codes.keys():
        codes_str += f",{key},{codes[key]}"

    # combine all metadata together into a comma-separated string and convert to binary
    string = f"{dims[0]},{dims[1]},{padding}{codes}"
    b_string = ''.join(format(ord(char), '08b') for char in string)

    # pad with zeros to ensure length is a multiple of 8
    padding = 8-(len(b_string)%8)
    b_string = '0'*padding + b_string

    return b_string


def convert_to_bytes(string):
    """
    Convert a bit string to bytes.

    Args:
        string (str): a bit string containing 0s and 1s. Length must be a multiple of 8.
    
    Returns:
        bytes: byte data equivalent to bit string.
    """
    if len(string)%8 != 0:
        raise ValueError("String not padded correctly")
    
    byte_list = []
    for i in range(0, len(string), 8):
        byte = string[i:i+8]
        byte_list.append(int(byte, 2))

    return bytes(byte_list)


def write_to_file(byte_list, metadata, path):    
    """
    Writes metadata and encoded image data to a file at the specified path,
    separated by the bytes b'\xAA\xBB\xCC'.

    Args:
        byte_list (bytes): encoded image data, as bytes.

        metadata (bytes): metadata string, as bytes.

        path (str): path where byte file will be saved.
    """
    separation_code = b'\xAA\xBB\xCC'
    with open(path, 'wb') as f:
        f.write(metadata)
        f.write(separation_code)
        f.write(byte_list)