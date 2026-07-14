'''
OCR = Optical C(level) Recognition
By BrownieO
Reads a level image and makes an array of tile IDs.
It also can sort the IDs by frequency.
'''
import argparse
import numpy as np
from pathlib import Path
from PIL import Image, ImageChops

parser = argparse.ArgumentParser(description="Reads a level image and makes an array of tile IDs.")
parser.add_argument("-f", "--file", help="set the input file path")
parser.add_argument("-l", "--level", action="store_true", help="output a full level array")
parser.add_argument("-p", "--palette", action="store_true", help="output an image with all the unique tiles")
parser.add_argument("-s", "--sort", action="store_true", help="sort the tile IDs by frequency")
args = parser.parse_args()

if not args.level and not args.palette and not args.sort:
    parser.print_help()
    if args.file:
        print("Please select a task.")
    quit()

def split_image_into_tiles(img):
    tiles = []
    unique = []

    for r in range(rows):
        for c in range(cols):
            left = c * tile_width
            top = r * tile_height
            right = (c + 1) * tile_width
            bottom = (r + 1) * tile_height

            tile = img.crop((left, top, right, bottom))

            still_unique = True

            # If there's a tile image equal to the current one, append its index to the "tiles" array.
            for item in unique:
                diff = ImageChops.difference(item, tile)
                if not diff.getbbox():
                    tiles.append(unique.index(item))
                    still_unique = False
                    break

            # Else, save a new image and append the new index.
            if still_unique:
                unique.append(tile)
                tiles.append(len(unique)-1)

    return tiles, unique

def create_image_chain(images):
    widths, heights = zip(*(i.size for i in images)) # The asterisk unpacks each tile image

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    return new_im

def sort_tiles(level, unique_ids, freq):
    sorted_indices = np.argsort(freq)[::-1]
    sorted_unique_ids = unique_ids[sorted_indices]
    replacements_dict = {tile_id: n for n, tile_id in enumerate(sorted_unique_ids)}
    n = 0
    for tile_id in sorted_unique_ids:
        replacements_dict[tile_id] = n
        n += 1
    m = 0
    for tile_id in level:
        level[m] = replacements_dict[tile_id]
        m += 1
    return level, sorted_unique_ids

def create_palette(unique_ids, unique_tiles):
    image_chain = []
    n = 0
    for tile_id in unique_ids:
        image_chain.append(unique_tiles[tile_id])

    return create_image_chain(image_chain)


img = Image.open(args.file)
img_width, img_height = img.size

tile_width = 16
tile_height = 16

cols = img_width // tile_width
rows = img_height // tile_height


level, unique_tiles = split_image_into_tiles(img)

unique_ids, freq = np.unique(level, return_counts=True)

if args.sort:
    level, unique_ids = sort_tiles(level, unique_ids, freq)

if args.palette:
    im = create_palette(unique_ids, unique_tiles)

    output_palette_path = Path(args.file).parent / (Path(args.file).stem + "_palette.png")
    im.save(output_palette_path)

    print(f"Palette saved to {output_palette_path}")

if args.level:
    level = np.reshape(level, (rows, cols))

    level_formatted = level
    level_formatted = np.rot90(level_formatted, 3)
    level_formatted = np.fliplr(level_formatted)

    output_path = Path(args.file).parent / (Path(args.file).stem + ".csv")
    np.savetxt(output_path, level_formatted, fmt="%d", delimiter=",")
    
    print(f"Level array saved to {output_path}")
