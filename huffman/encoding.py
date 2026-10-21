from PIL import Image

"""
"""
def encode_image(img_dir):
    img = Image.open(img_dir).convert('RGB') #'L' for grayscale
    RGB = split_rgb(img)

    for color in RGB:
        freqs = map_freqs(color)
        tree = generate_tree(freqs)
        codes = generate_codes(tree)
        print(codes)
    
    

"""
"""
def split_rgb(img):
    width, height = img.size
    pixels = img.load()
    
    [R, G, B] = [[] for i in range(3)]

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x,y]
            R.append(r)
            G.append(g)
            B.append(b)

    return R, G, B


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
