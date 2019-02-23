
from kivy.graphics.texture import Texture
from kivy.uix.label import CoreLabel
from typing import Dict, Tuple

texture_dict: Dict[Tuple[int, int, str], Texture] = {}


def get_text_texture(x: int, y: int, text: str):

    if (x, y, text) in texture_dict:
        return texture_dict[(x, y, text)]

    font_size = 10

    result_texture = gen_texture(text, font_size)
    diff_size = min(x - result_texture.width, y - result_texture.height)

    while diff_size >= 2:
        result_texture = gen_texture(text, font_size)

        font_size = int(font_size * min(x / result_texture.width, y / result_texture.height))
        diff_size = min(x - result_texture.width, y - result_texture.height)

    texture_dict[(x, y, text)] = result_texture

    return result_texture


def gen_texture(text: str, font_size: int):
    num_label = CoreLabel(text=text, font_size=font_size)
    num_label.refresh()
    return num_label.texture



