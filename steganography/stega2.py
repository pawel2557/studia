import sys
import math
import os
from os import path
import cv2
import numpy as np
import random


BITS = 2
HIGH_BITS = 256 - (1 << BITS)
LOW_BITS = (1 << BITS) - 1
BYTES_PER_BYTE = math.ceil(8 / BITS)
FLAG = '%'


def list_images(directory):
    images = [f for f in os.listdir(directory) if f.endswith(('.jpg', '.png', '.jpeg', '.bmp'))]
    if not images:
        print("No images found in the directory.")
        return None

    print("Available images:")
    for idx, img in enumerate(images):
        print(f"{idx + 1}. {img}")

    while True:
        try:
            choice = int(input("Select an image by number: ")) - 1
            if 0 <= choice < len(images):
                return path.join(directory, images[choice])
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def generate_permutation(size, seed):
    indices = list(range(size))
    random.seed(seed)
    random.shuffle(indices)
    return indices


def insert(img_path, msg):
    try:
        seed = int(input("Enter integer key for permutation (seed): "))
        img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR)
        if img is None:
            raise FileNotFoundError("Image not found. Check the file path.")

        ori_shape = img.shape
        max_bytes = ori_shape[0] * ori_shape[1] // BYTES_PER_BYTE
        msg = '{}{}{}'.format(len(msg), FLAG, msg)

        if len(msg) > max_bytes:
            raise ValueError(f"Message too large. Max capacity: {max_bytes} characters.")

        data = np.reshape(img, -1)
        total_slots = len(data) // BYTES_PER_BYTE
        perm = generate_permutation(total_slots, seed)

        for real_idx, val in zip(perm, msg):
            encode(data[real_idx * BYTES_PER_BYTE: (real_idx + 1) * BYTES_PER_BYTE], val)

        img = np.reshape(data, ori_shape)
        filename, ext = path.splitext(img_path)
        filename += '_lsb_embedded' + ext
        cv2.imwrite(filename, img)
        print(f"Successfully embedded message into {filename}")
        return filename
    except Exception as e:
        print(f"Error: {e}")


def encode(block, data):
    data = ord(data)
    for idx in range(len(block)):
        block[idx] &= HIGH_BITS
        block[idx] |= (data >> (BITS * idx)) & LOW_BITS


def extract(img_path):
    try:
        seed = int(input("Enter integer key for permutation (seed): "))
        img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR)
        if img is None:
            raise FileNotFoundError("Image not found. Check the file path.")

        data = np.reshape(img, -1)
        total_slots = len(data) // BYTES_PER_BYTE
        perm = generate_permutation(total_slots, seed)

        message = ""
        idx = 0
        while True:
            real_idx = perm[idx]
            char_code = 0
            for i in range(BYTES_PER_BYTE):
                char_code |= (data[real_idx * BYTES_PER_BYTE + i] & LOW_BITS) << (BITS * i)
            idx += 1
            char = chr(char_code)
            if char == FLAG:
                break
            message += char

        length = int(message)
        extracted_msg = ""
        for _ in range(length):
            real_idx = perm[idx]
            char_code = 0
            for i in range(BYTES_PER_BYTE):
                char_code |= (data[real_idx * BYTES_PER_BYTE + i] & LOW_BITS) << (BITS * i)
            idx += 1
            extracted_msg += chr(char_code)

        print("Extracted message:", extracted_msg)
        return extracted_msg
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    default_dir = "./assets"
    user_dir = input(f"Enter directory (or press Enter to use default '{default_dir}'): ").strip()
    assets_dir = user_dir if user_dir else default_dir

    while True:
        print("\nChoose an option:")
        print("1. Encode message into image")
        print("2. Decode message from image")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            img_path = list_images(assets_dir)
            if img_path:
                msg = input("Enter the message to hide: ")
                insert(img_path, msg)
        elif choice == '2':
            img_path = list_images(assets_dir)
            if img_path:
                extract(img_path)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")