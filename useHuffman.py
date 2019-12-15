from huffman import Huffman
import sys

path = 'images\\sample.bmp'

h = Huffman(path)

output_path = h.compress()
print("Compressed file path: " + output_path)

decom_path = h.decompress(output_path)
print("Decompressed file path: " + decom_path)
