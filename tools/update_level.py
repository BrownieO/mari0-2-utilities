import argparse
from pprint import pformat
from typing import Any

ENTITY_LIST = [
    None,           # 0
    None,           # 1
    "mushroom",     # 2
    "one_up",       # 3
    "starman",      # 4
    None,           # 5
    "goomba",       # 6
    "koopa",        # 7
    "spawn",        # 8
    "goomba",       # 9
    "koopa",        # 10
    "goal_block",   # 11
    "koopa_red",    # 12
    "koopa_red",    # 13
]

BACKGROUND_LIST = [
    None,
    [92, 148, 252],   # sky blue
    [0, 0, 0],        # black
    [32, 56, 236],    # blue
    [0],
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Port Mari0 levels to Mari0 2."
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="Path to the level file",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional path to write the converted level (prints to stdout if omitted)",
    )
    return parser.parse_args()

def load_level(file_path: str):
    with open(file_path, "r", newline="") as f:
        return f.read()


def save_output(content: str, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

def parse_level(raw: str):
    rows = raw.strip().split(";")
    return [row.split(",") for row in rows if row]

def separate_into_columns(flat_list: list[str], height: int):
    width = len(flat_list) // height
    columns: list[list[str]] = []

    for col in range(width):
        column = [flat_list[row * width + col] for row in range(height)]
        columns.append(column)

    return columns

def parse_columns(columns: list[list[str]]):
    tiles: list[list[int]] = []
    entities: list[list[dict[str, Any]]] = []

    for x, col in enumerate(columns):
        new_col: list[int] = []
        for y, element in enumerate(col):
            parts = element.split("-")
            tile_id = int(parts[0])

            new_col.append(0 if tile_id == 1 else tile_id)

            if len(parts) > 1:
                entity_idx = int(parts[1])
                if 0 <= entity_idx < len(ENTITY_LIST) and ENTITY_LIST[entity_idx]:
                    entity_name = ENTITY_LIST[entity_idx]
                    entities.append([
                        {"type": entity_name},
                        {"x": x + 1},
                        {"y": y + 1},
                    ])

        tiles.append(new_col)
        
    return tiles, entities

def convert_to_lua(python_repr: str):
    replacements = {
        "{'": "",
        "{": "",
        "':": "=",
        "}": "",
        "[": "{",
        "]": "}",
        " 'l": "l",
        " 'e": "e",
        " 'b": "b",
    }

    for old, new in replacements.items():
        python_repr = python_repr.replace(old, new)

    return "return {\n" + python_repr + "\n}"

def generate_new_level(parsed: list[list[str]]):
    height = int(parsed[1][0].split("=")[1])

    columns = separate_into_columns(parsed[0], height)
    tiles, entities = parse_columns(columns)

    bg_index = int(parsed[2][0].split("=")[1])
    background = BACKGROUND_LIST[bg_index] if 0 <= bg_index < len(BACKGROUND_LIST) else None

    data: dict[str, Any] = {
        "tileMaps": ["smb", "portal-legacy"],
        "lookups": [[1, id_] for id_ in range(1, 133)] + [[2, id_] for id_ in range(1, 88)],
        "layers": [
            [{"x": 0}, {"y": 0}, {"map": tiles}],
        ],
        "entities": entities,
        "backgroundColor": background,
    }

    pretty = pformat(data, width=999, sort_dicts=False)
    return convert_to_lua(pretty)

def main():
    args = parse_args()
    raw = load_level(args.file)
    parsed = parse_level(raw)
    new_level = generate_new_level(parsed)

    if args.output:
        save_output(new_level, args.output)
    else:
        print(new_level)

if __name__ == "__main__":
    main()
