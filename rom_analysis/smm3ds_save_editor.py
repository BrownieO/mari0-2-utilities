"""
Super Mario Maker for Nintendo 3DS Save Editor
Created by RealSweeper3
Port to Python by BrownieO
https://github.com/RealSweeper3/SMM3DSSE/tree/master
"""
import os
import sys
import struct
import argparse

FILESIZE_PROGRESS = 0x8018
ADDIFF_PROGRESS = 0x8000

def addcrc(data: bytes, i: int, diff: int) -> int:
    count = i >> 1

    hash_value = 1

    for j in range(count):
        value = int.from_bytes(data[j * 2:j * 2 + 2], "little")
        hash_value += value

    return diff + hash_value

def fix_checksum(file_path: str):
    with open(file_path, 'rb+') as f:
        data = f.read(FILESIZE_PROGRESS)
        if len(data) < FILESIZE_PROGRESS:
            print("File too small")
            return
        checksum_data = data[0x18:]
        checksum = addcrc(checksum_data, FILESIZE_PROGRESS - 0x18, ADDIFF_PROGRESS)
        f.seek(0)
        f.write(struct.pack('<I', checksum))
    print("Checksum fixed")

def all_items(file_path: str):
    with open(file_path, 'rb+') as f:
        f.seek(0x4252)
        f.write(b'\x13')  # 19
    print("All items unlocked")

def all_medals(file_path: str):
    with open(file_path, 'rb+') as f:
        for i in range(100):
            f.seek(0x4700 + i)
            f.write(b'\x07')  # 7
    print("All medals unlocked")

def backup_medals(file_path: str):
    with open(file_path, 'rb') as f:
        f.seek(0x4700)
        medals = f.read(99)
    with open('medals.bin', 'wb') as f:
        f.write(medals)
    print("Medals backed up to medals.bin")

def restore_medals(file_path: str):
    if not os.path.exists('medals.bin'):
        print("medals.bin not found")
        return
    with open('medals.bin', 'rb') as f:
        medals = f.read(99)
    with open(file_path, 'rb+') as f:
        f.seek(0x4700)
        f.write(medals)
    print("Medals restored")

def edit_lives(file_path: str):
    try:
        lives = int(input("Enter lives (1-100): "))
        if not 1 <= lives <= 100:
            print("Invalid lives value")
            return
        with open(file_path, 'rb+') as f:
            f.seek(0x4250)
            f.write(struct.pack('b', lives))
        print(f"Lives set to {lives}")
    except ValueError:
        print("Invalid input")

def main():
    parser = argparse.ArgumentParser(description="Super Mario Maker 3DS Save Editor")
    parser.add_argument("file", help="Path to the Progress save file")
    parser.add_argument("--all-medals", action="store_true", help="Unlock all medals")
    parser.add_argument("--all-items", action="store_true", help="Unlock all items")
    parser.add_argument("--backup-medals", action="store_true", help="Backup medals")
    parser.add_argument("--restore-medals", action="store_true", help="Restore medals")
    parser.add_argument("--edit-lives", action="store_true", help="Edit lives")
    parser.add_argument("--fix-checksum", action="store_true", help="Fix checksum (run last)")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("Save file not found")
        exit()

    if args.all_medals:
        all_medals(args.file)
    if args.all_items:
        all_items(args.file)
    if args.backup_medals:
        backup_medals(args.file)
    if args.restore_medals:
        restore_medals(args.file)
    if args.edit_lives:
        edit_lives(args.file)
    if args.fix_checksum:
        fix_checksum(args.file)

    print("Ready. Please backup your original save file.")

if __name__ == "__main__":
    main()
