import cv2
import numpy as np
import random

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def generate_coords(h, w, num_bits, r):
    coords = []
    for _ in range(num_bits):
        bit_coords = []
        for _ in range(r):
            y = random.randint(1, h - 2)
            x = random.randint(1, w - 2)
            bit_coords.append((y, x))
        coords.append(bit_coords)
    return coords

def embed_message(image_path, message, output_path, alpha=0.07, r=9):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found.")
    h, w, _ = img.shape
    bits = text_to_bits(message)
    total_bits = len(bits)
    max_bits = (h - 2) * (w - 2) // r
    if total_bits > max_bits:
        raise ValueError("Message too long for this image.")

    img = img.astype(np.float32)
    Y = 0.298 * img[:, :, 2] + 0.586 * img[:, :, 1] + 0.114 * img[:, :, 0]
    coords = generate_coords(h, w, total_bits, r)

    for i, bit in enumerate(bits):
        for y, x in coords[i]:
            delta = alpha * Y[y, x]
            if bit == '1':
                img[y, x, 0] = np.clip(img[y, x, 0] + delta, 0, 255)
            else:
                img[y, x, 0] = np.clip(img[y, x, 0] - delta, 0, 255)

    cv2.imwrite(output_path, img.astype(np.uint8))
    print("Message embedded and saved to", output_path)
    return coords, len(message)

def extract_message(image_path, coords, msg_len, r=9):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found.")
    img = img.astype(np.float32)
    B = img[:, :, 0]

    bits = []
    for i in range(msg_len * 8):
        votes = []
        for y, x in coords[i]:
            neighbors = [B[y-1, x], B[y+1, x], B[y, x-1], B[y, x+1]]
            pred = np.mean(neighbors)
            delta = B[y, x] - pred
            bit = 1 if delta > 0 else 0
            votes.append(bit)
        majority = 1 if votes.count(1) > votes.count(0) else 0
        bits.append(str(majority))

    return bits_to_text(''.join(bits))

# Przykład użycia
if __name__ == "__main__":
    message = "Jestem Pawel"
    coords, length = embed_message('assets/images.bmp', message, 'assets/output_kjb.bmp')
    recovered = extract_message('assets/output_kjb.bmp', coords, length)
    print("Recovered:", recovered)
