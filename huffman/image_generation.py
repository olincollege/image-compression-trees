"""
Contains a function for generating a random image to use for testing.
"""

from PIL import Image
from random import randrange, choice

def generate_image(side_length, color_count):
    """
    Generates and saves a square image with Pillow, with a specified side length and number of
    colors. The colors are distributed randomly and in random amounts throughout the image.

    Args:
        side_length (int): the length of one of the square sides of the image.

        color_count (int): the total number of colors present in the image.
    """
    colors = [tuple([randrange(256) for _ in range(3)]) for _ in range(color_count)]

    image = Image.new(mode="RGB", size=(side_length, side_length))
    pixels = image.load()

    for i in range(side_length):
        for j in range(side_length):
            pixels[i, j] = choice(colors)

    image.save(f"data/{side_length}x{side_length}_{color_count}.jpeg", format="jpeg", quality=95, optimize=False)