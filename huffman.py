import heapq
import os
from PIL import Image
import numpy as np

class HeapNode:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None
        
    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        if(other == None):
            return False
        if(not isinstance(other, HeapNode)):
            return False
        return self.freq == other.freq

class Huffman:
    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.shape = None

    def frequency_dict(self, array):
        frequency = {}
        for value in array:
            if not value in frequency:
                frequency[value] = 0
            frequency[value] += 1
        return frequency
    
    def make_heap(self, frequency):
        for key in frequency:
            node = HeapNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            heapq.heappush(self.heap, merged)            

    def make_codes_helper(self, root, current_code):
        if(root == None):
            return

        if(root.value != None):
            self.codes[root.value] = current_code
            self.reverse_mapping[current_code] = root.value
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")


    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_img(self, img):
        encoded_string = ""
        for value in img:
            encoded_string += self.codes[value]
        width, hight, depth = self.shape
        shape_info = "{0:016b}{0:016b}{0:04b}".format(width, hight, depth)
        encoded_string = shape_info + encoded_string
        return encoded_string

    def pad_encoded_img(self, encoded_img, length):
        extra_padding = 8 - len(encoded_img) % 8
        for i in range(extra_padding):
            encoded_img += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_img = length + padded_info + encoded_img
        return encoded_img

    def get_byte_array(self, padded_encoded_img):
        if(len(padded_encoded_img) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_img), 8):
            byte = padded_encoded_img[i:i+8]
            b.append(int(byte, 2))
        return b

    def average_len(self, frequency):
        totel = 0
        length = 0
        for i in frequency:
            totel = totel + frequency[i]
        for j in frequency:
            length = length + len(self.codes[j])*frequency[j]
            avg_len = length/totel

        return avg_len

    def convert_img_text(self, img):
        string = ''
        for i in img:
            str1 = str(i)
            if(len(str1)==2):
                str1 = '0' + str1
            if(len(str1)==1):
                str1 = '00' + str1
            if(len(str1)==3):
                string = string + str1
            else:
                print("error in encoding image")
                break
        return string

    def get_info_bytes(self):
        lst1 = []
        lst2 = []
        str3 = ''
        for i in self.codes:
            lst1.append(i)
            lst2.append(len(self.codes[i]))
            str3 = str3 + str(self.codes[i])
        str1 = self.convert_img_text(lst1)
        str2 = ''
        for i in lst2:
            str2 = str2 + str(i)

        #print(str1,str2,str3)
        string =  str1 + str2 + str3
        bytestr = bytes(string, 'utf-8')
        length = "{0:016b}".format(len(bytestr))
       # print(type(length))
        return bytestr,length

    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"

        file = Image.open(self.path)

        img = np.array(file)
        #print(img)
        self.shape = img.shape
        img = img.flatten()
        print(len(img))
        frequency = self.frequency_dict(img)
        self.make_heap(frequency)
        #print(frequency)
        self.merge_nodes()
        self.make_codes()
        print(self.average_len(frequency))
        print('50%')
        encoded_bytes, length = self.get_info_bytes()
        encoded_img = self.get_encoded_img(img)
        print('75%')
        
        padded_encoded_img = self.pad_encoded_img(encoded_img, length)
        print('80%')
        
        byte_array = self.get_byte_array(padded_encoded_img)
        
        byte_string = byte_array + encoded_bytes
        print(len(byte_string))
        print(len(byte_array))
        output = open(output_path, 'wb')
        output.write(bytes(byte_string))

        print("Compressed")
        return output_path

    def remove_padding(self, padded_encoded_img):
        padded_info = padded_encoded_img[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_img = padded_encoded_img[8:] 
        encoded_img = padded_encoded_img[:-1*extra_padding]

        return encoded_img

    def decode_img(self, encoded_img):
        current_code = ""
        decoded_img = []

        for bit in encoded_img:
            current_code += bit
            if(current_code in self.reverse_mapping):
                value = self.reverse_mapping[current_code]
                decoded_img.append(value)
                current_code = ""
        return decoded_img

    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + file_extension

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while(len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            encoded_img = self.remove_padding(bit_string)

            decompressed_img = self.decode_img(encoded_img)
            decompressed_img = np.resize(decompressed_img, self.shape)
            #print(decompressed_img)
            im = Image.fromarray(decompressed_img)
            im.save(output_path)

        print("Decompressed")
        return output_path