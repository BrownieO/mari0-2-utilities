import argparse
import csv
import json
from pprint import pformat

entity_list = [None, None, "mushroom", "one_up", "starman", None, "goomba", "koopa", "spawn", "goomba", "koopa", "goal_block", "koopa_red", "koopa_red"]

background_list = [
    None,
    [92, 148, 252],
    [0, 0, 0],
    [32, 56, 2436],
    [0]
]

def parse_args():
    parser = argparse.ArgumentParser(description='Port Mari0 levels to Mari0 2.')
    parser.add_argument('-f', "--file", type=str, required=True, help='Path to the ID list')
    parser.add_argument('-o', "--output", type=str, default=None, help='Output file to save the result (optional)')
    
    return parser.parse_args()

def load_level(file_path):
    with open(file_path, 'r', newline = '') as f:
        return f.read()

def parse_level(string):
    data = []
    string = string.split(';')
    
    for row in string:
        data.append(row.split(','))
        
    return data

def separate_into_columns(my_list, height):
    width = len(my_list) // height
    columns = []

    for col in range(width):
        column = []
        for row in range(height):
            column.append(my_list[row * width + col])
        columns.append(column)

    return columns

def parse_columns(my_list):
    tiles = []
    entities = []
    
    for x, col in enumerate(my_list):
        new_col = []
        for y, element in enumerate(col):
            tile_id = int(element.split('-')[0])
            if tile_id == 1:
                new_col.append(0)
            else:
                new_col.append(tile_id)
            if len(element.split('-')) > 1:
                if int(element.split('-')[1]) <= len(entity_list):
                    if entity_list[int(element.split('-')[1])]:
                        entity_name = entity_list[int(element.split('-')[1])]
                        entities.append([{'type': entity_name}, {'x': x+1}, {'y': y+1}])
            
        tiles.append(new_col)
    
    return tiles, entities

def convert_to_lua(string):
    replacements = {
        "{'" : "",
        "{" : "",
        "':" : "=",
        "}" : "",
        "[" : "{",
        "]" : "}",
        
        " 'l" : "l",
        " 'e" : "e",
        " 'b" : "b"
        
    }
    for old_str, new_str in replacements.items():
        string = string.replace(old_str, new_str)
    
    return 'return {\n' + string + '\n}'

def generate_new_level(old_level):
    columns = separate_into_columns(old_level[0], int(level[1][0].split('=')[1]))
    tiles, entities = parse_columns(columns)
    data = {}
    data['tileMaps'] = ['smb']
    data['lookups'] = []
    for id in range(1, 130):
        data['lookups'].append([1, id])
    data['layers'] = []
    data['layers'].append([{'x': 0},{'y': 0},{'map':tiles}])
    data['entities'] = entities
    data['backgroundColor'] = background_list[int(level[2][0].split('=')[1])]
    
    data = pformat(data, width=999,sort_dicts=False)
    data = convert_to_lua(data)
    
    return data

def save_output(processed_map, output_file):
    with open(output_file, 'w') as f:
        for line in processed_map:
            f.write(line + '\n')

args = parse_args()
level = parse_level(load_level(args.file))

new_level = generate_new_level(level)

if args.output:
    save_output(new_level, args.output)
else:

    print(new_level)
