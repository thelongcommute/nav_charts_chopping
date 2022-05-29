import sys
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None

if __name__ == "__main__":
    print(sys.argv)
    in_file_path = sys.argv[1]
    im_raw = Image.open(in_file_path)
    left_edge = int(sys.argv[2])
    top_edge = int(sys.argv[3])
    right_edge = int(sys.argv[4])
    bot_edge = int(sys.argv[5])
    box = (left_edge, top_edge, right_edge, bot_edge)

    file_path_no_suffix = in_file_path.split(".tif")[0]
    out_file_path_segmented = file_path_no_suffix + "_segmented.tif"
    out_file_path_cropped = file_path_no_suffix + "_cropped.tif"

    im = im_raw.copy()
    im_draw = ImageDraw.Draw(im)
    im_draw.rectangle(box, outline="red", width=10)
    im.save(out_file_path_segmented)
    region = im_raw.crop(box)
    region.save(out_file_path_cropped)
