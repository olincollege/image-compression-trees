from PIL import Image
from random import randrange, choice

def generate_image(side_length, color_count):
    """
    """
    colors = [tuple([randrange(256) for _ in range(3)]) for _ in range(color_count)]

    image = Image.new(mode="RGB", size=(side_length, side_length))
    pixels = image.load()

    for i in range(side_length):
        for j in range(side_length):
            pixels[i, j] = choice(colors)

    image.save(f"data/{side_length}x{side_length}_{color_count}.png", format="png")