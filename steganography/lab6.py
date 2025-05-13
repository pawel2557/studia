import numpy as np
import wave

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def hide_message_lsb(input_wav, output_wav, message):
    with wave.open(input_wav, 'rb') as wav_in:
        params = wav_in.getparams()
        n_frames = wav_in.getnframes()
        audio_data = np.frombuffer(wav_in.readframes(n_frames), dtype=np.int16)

    bits = text_to_bits(message)
    bits += '00000000'  # terminator (null char)

    if len(bits) > len(audio_data):
        raise ValueError("Message too long to hide in this audio")

    modified = np.copy(audio_data)
    for i, bit in enumerate(bits):
        modified[i] = (modified[i] & ~1) | int(bit)

    with wave.open(output_wav, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(modified.tobytes())

def extract_message_lsb(stego_wav):
    with wave.open(stego_wav, 'rb') as wav_in:
        n_frames = wav_in.getnframes()
        audio_data = np.frombuffer(wav_in.readframes(n_frames), dtype=np.int16)

    bits = ''.join([str(sample & 1) for sample in audio_data])
    bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    chars = []

    for byte in bytes_list:
        if byte == '00000000':
            break
        chars.append(chr(int(byte, 2)))

    return ''.join(chars)

# Przykład użycia
if __name__ == '__main__':
    hide_message_lsb('./assets/input.wav', './assets/output.wav', 'Steganografia audio LSB!')
    message = extract_message_lsb('./assets/output.wav')
    print("Extracted message:", message)
