import numpy as np
import cv2
from scipy.fftpack import dct, idct

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    height, width = img.shape
    height -= height % 8
    width -= width % 8
    img = cv2.resize(img, (width, height))
    return img

def split_into_blocks(img):
    blocks = []
    height, width = img.shape
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            blocks.append(img[i:i+8, j:j+8].astype(np.float32))
    return blocks

def merge_blocks(blocks, image_shape):
    height, width = image_shape
    img = np.zeros((height, width), dtype=np.float32)
    idx = 0
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            img[i:i+8, j:j+8] = blocks[idx]
            idx += 1
    return img

def embed_data(blocks, message_bits, alpha=100):
    embedded_blocks = []
    for idx, block in enumerate(blocks):
        dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
        if idx < len(message_bits):
            x, y = 3, 4
            if message_bits[idx] == '1':
                dct_block[x, y] = dct_block[y, x] + alpha
            else:
                dct_block[x, y] = dct_block[y, x] - alpha
        idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
        embedded_blocks.append(idct_block)
    return embedded_blocks

def extract_data(blocks, bit_count):
    extracted_bits = ''
    for idx, block in enumerate(blocks):
        if idx >= bit_count:
            break
        dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
        x, y = 3, 4
        extracted_bits += '1' if dct_block[x, y] > dct_block[y, x] else '0'
    return extracted_bits

def message_to_bits(message):
    return ''.join(f'{ord(c):08b}' for c in message)

def bits_to_message(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def int_to_bits(n, bit_len=16):
    return f'{n:0{bit_len}b}'

def bits_to_int(bits):
    return int(bits, 2)

if __name__ == "__main__":
    image_path = './assets/images.jpg'              # oryginał może być JPEG
    output_path = './assets/output_image.png'       # MUSI być PNG
    message = "Hello!"

    img = preprocess_image(image_path)
    blocks = split_into_blocks(img)

    message_bits = message_to_bits(message)
    message_length_bits = int_to_bits(len(message_bits), bit_len=16)
    full_bits = message_length_bits + message_bits

    if len(full_bits) > len(blocks):
        raise ValueError("Image too small to hold the message.")

    embedded_blocks = embed_data(blocks, full_bits, alpha=100)
    embedded_img = merge_blocks(embedded_blocks, img.shape)

    embedded_img_clipped = np.clip(embedded_img, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, embedded_img_clipped)

    extracted_img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    extracted_blocks = split_into_blocks(extracted_img)

    length_bits = extract_data(extracted_blocks, 16)
    message_bit_length = bits_to_int(length_bits)

    extracted_bits = extract_data(extracted_blocks[16:], message_bit_length)
    extracted_message = bits_to_message(extracted_bits)

    print("Original message:", message)
    print("Extracted message:", extracted_message)
    if extracted_message != message:
        print("WARNING: Extracted message may be corrupted!")
