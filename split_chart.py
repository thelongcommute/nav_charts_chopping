from PIL import Image, ImageDraw, ImageFont
import math
import re
import json

Image.MAX_IMAGE_PIXELS = None

config = {
    "ruler_width": 242,
    "ruler_on_right": True,  # False if on left
    "ruler_on_bottom": True,
    "num_slices_horizontal": 2,
    "num_slices_vertical": 4,
    "input_filepath": "3936/input data/3936_raw.tif"
    # "vert_overlap": 800,

}

colours = ["yellow", "red", "purple", "blue", "green", "pink", "orange", "cyan", "Indigo", "DarkSalmon", "Khaki",
           "Lime", "DarkRed", "YellowGreen", "Aquamarine", "Black", "GoldenRod"]


def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


if __name__ == "__main__":
    im = Image.open(config["input_filepath"])
    map_name = re.search(r"(?<=input data/).*?(?=_raw)", config["input_filepath"]).group(0)
    base_path = re.search(r".*?(?=input data/)", config["input_filepath"]).group(0)
    print(f"base path {base_path}")
    w, h = im.size

    config["vert_overlap"] = h // (8 * config["num_slices_vertical"])
    print(im.format, im.size, im.mode)

    base_height = (h - config["ruler_width"] + config["vert_overlap"] *
                   (config["num_slices_vertical"] - 1)) / config["num_slices_vertical"]
    base_width = base_height * 17 / 11
    base_height = math.floor(base_height)
    base_width = math.floor(base_width)

    horiz_overlap = math.floor((base_width * config["num_slices_horizontal"] - w + config["ruler_width"]) /
                               (config["num_slices_horizontal"] - 1))
    print(f"base width: {base_width}")
    print(f"base height: {base_height}")
    print(f"horiz overlap: {horiz_overlap}")
    boxes = []
    output = []

    left_edge_offset = 0
    top_edge_offset = 0
    if config["ruler_on_right"]:
        ruler_pos_horiz = (w - config["ruler_width"], w)
    else:
        left_edge_offset = config["ruler_width"]
        ruler_pos_horiz = (0, config["ruler_width"])
    if config["ruler_on_bottom"]:
        ruler_pos_vert = (h - config["ruler_width"], h)
    else:
        top_edge_offset = config["ruler_width"]
        ruler_pos_vert = (0, config["ruler_width"])

    im_boxes_indicated = im.copy()
    im_boxes_indicated_draw = ImageDraw.Draw(im_boxes_indicated)

    font_name = "Fonts/roboto/Roboto-Black.ttf"
    font_size = 100  # 120
    font = ImageFont.truetype(font_name, font_size)

    for i in range(config["num_slices_horizontal"]):
        for j in range(config["num_slices_vertical"]):
            left_edge = i * (base_width - horiz_overlap) + left_edge_offset
            right_edge = (i + 1) * base_width - i * horiz_overlap + left_edge_offset
            top_edge = j * (base_height - config["vert_overlap"]) + top_edge_offset
            bot_edge = (j + 1) * base_height - j * config["vert_overlap"] + top_edge_offset

            box = (left_edge, top_edge, right_edge, bot_edge)
            segment_name = f"{chr(i + 65)}{j}"
            file_out = f"{base_path}output data/{map_name}_{segment_name}.tif"
            region = im.crop(box)
            region = get_concat_h(region, im.crop((ruler_pos_horiz[0], top_edge, ruler_pos_horiz[1], bot_edge)))
            region = get_concat_v(region, im.crop((left_edge, ruler_pos_vert[0], right_edge, ruler_pos_vert[1])))

            region_draw = ImageDraw.Draw(region)
            region_draw.rectangle((base_width, base_height, base_width + config["ruler_width"],
                                   base_height + config["ruler_width"]), fill="white")
            region_draw.text((base_width + 20, base_height + 50), f"{map_name} \n {segment_name}", font=font,
                             fill=(255, 0, 0))
            region.save(file_out)
            boxes.append(box)
            im_boxes_indicated_draw.rectangle(box, outline=colours.pop(), width=50)

    print(f"Number of boxes {len(boxes)}")
    print(boxes)
    file_out = f"{base_path}output data/{map_name}_overview.tif"
    im_boxes_indicated.save(file_out)

    with open(f"{base_path}output data/{map_name}_config.json", "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)
