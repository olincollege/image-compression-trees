from PIL import Image

"""
"""
def encode_image(img_dir):
    img = Image.open(img_dir).convert('RGB') #'L' for grayscale
    R, G, B = split_rgb(img)

    R_freqs = map_freqs(R)
    R_codes = generate_codes(R_freqs)

    G_freqs = map_freqs(G)
    G_codes = generate_codes(G_freqs)

    B_freqs = map_freqs(B)
    B_codes = generate_codes(B_freqs)
    
    

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
def generate_codes(freqs):
    vals = list(freqs.keys())
    vals.sort(key=lambda val: freqs[val])
    