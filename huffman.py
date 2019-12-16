import heapq
import os
from PIL import Image
import numpy as np

class HeapNode:
    def __init__(self, value, freq, n):
        self.value = value
        self.freq = freq
        self.branch = [None]*n
        
        
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
    
    def freq_dict_padding(self, frequency):
        index = len(frequency)
        if(index%9==0):
            return frequency
        new_index = (int(index/9) + 1)*9
        for key in range(index+1,new_index+2):
            frequency[key] = 0
        return frequency

    def make_heap_d(self, frequency):
        for key in frequency:
            node1 = HeapNode(key, frequency[key], 10)
            heapq.heappush(self.heap, node1)
    
    def make_heap_b(self, frequency):
        for key in frequency:
            node2 = HeapNode(key, frequency[key], 2)
            heapq.heappush(self.heap, node2)

    def merge_nodes_b(self):
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged_b = HeapNode(None, node1.freq + node2.freq, 2)
            merged_b.branch[0] = node1
            merged_b.branch[1] = node2

            heapq.heappush(self.heap, merged_b)            

    def merge_nodes_d(self):
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            node3 = heapq.heappop(self.heap)
            node4 = heapq.heappop(self.heap)
            node5 = heapq.heappop(self.heap)
            node6 = heapq.heappop(self.heap)
            node7 = heapq.heappop(self.heap)
            node8 = heapq.heappop(self.heap)
            node9 = heapq.heappop(self.heap)
            node10 = heapq.heappop(self.heap)

            merged_d = HeapNode(None, node1.freq + node2.freq + node3.freq + node4.freq + node5.freq
                              + node6.freq + node7.freq + node8.freq + node9.freq + node10.freq, 10)
            merged_d.branch[0] = node1
            merged_d.branch[1] = node2
            merged_d.branch[2] = node3
            merged_d.branch[3] = node4
            merged_d.branch[4] = node5
            merged_d.branch[5] = node6
            merged_d.branch[6] = node7
            merged_d.branch[7] = node8
            merged_d.branch[8] = node9
            merged_d.branch[9] = node10
            #print('1')
            heapq.heappush(self.heap, merged_d)

    def make_codes_helper_b(self, root, current_code):
        ''' makes bineray codes'''
        if(root == None):
            return

        if(root.value != None):
            self.codes[root.value] = current_code
            self.reverse_mapping[current_code] = root.value
            return

        self.make_codes_helper_b(root.branch[0], current_code + "0")
        self.make_codes_helper_b(root.branch[1], current_code + "1")

    def make_codes_helper_d(self, root, current_code):
        ''' makes decimal codes '''
        if(root == None):
            return

        if(root.value != None):
            self.codes[root.value] = current_code
            self.reverse_mapping[current_code] = root.value
            return

        self.make_codes_helper_d(root.branch[0], current_code + "0")
        self.make_codes_helper_d(root.branch[1], current_code + "1")
        self.make_codes_helper_d(root.branch[2], current_code + "2")
        self.make_codes_helper_d(root.branch[3], current_code + "3")
        self.make_codes_helper_d(root.branch[4], current_code + "4")
        self.make_codes_helper_d(root.branch[5], current_code + "5")
        self.make_codes_helper_d(root.branch[6], current_code + "6")
        self.make_codes_helper_d(root.branch[7], current_code + "7")
        self.make_codes_helper_d(root.branch[8], current_code + "8")
        self.make_codes_helper_d(root.branch[9], current_code + "9")


    def make_codes_b(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper_b(root, current_code)

    def make_codes_d(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper_d(root, current_code)

    def get_encoded_img(self, img):
        encoded_string = ""
        for value in img:
            encoded_string += self.codes[value]
        return encoded_string

    def pad_encoded_img(self, encoded_img):
        extra_padding = 8 - len(encoded_img) % 8
        for i in range(extra_padding):
            encoded_img += "0"
        
        padded_info = "{0:08b}".format(extra_padding)
        encoded_img = padded_info + encoded_img
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

    def get_info_txt(self, encoded_text):
        string = ''
        for i in encoded_text:
            string = string + str(i)
			#string = string + str(self.codes[i])
        #info_len = len(string)
		
        encoded_text = encoded_text + string
        return encoded_text

    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"

        file = Image.open(self.path)

        img = np.array(file)
        #print(img)
        self.shape = img.shape
        img = img.flatten()
        print('no. of elements: ',len(img))
        frequency = self.frequency_dict(img)
        frequency = self.freq_dict_padding(frequency)
        self.make_heap_d(frequency)
        print('length of freq_dict: ',len(frequency))
        #print(frequency)
        self.merge_nodes_d()
        self.make_codes_d()
        alength = self.average_len(frequency)
        print('average length : ',self.average_len(frequency))
        print('compression ratio: ',8/alength)
        print('25%')
        encoded_img = self.get_encoded_img(img)
        print('50%')
        frequency_b = self.frequency_dict(encoded_img)
        padded_encoded_img = self.pad_encoded_img(encoded_img)
        self.make_heap_b(frequency_b)
        self.merge_nodes_b()
        self.make_codes_b()
        alength = self.average_len(frequency)
        print('average length b: ',self.average_len(frequency_b))
        print('compression ratio b: ',8/alength)
        print('70%')
        encoded_img_b = self.get_encoded_img(padded_encoded_img)
        padded_encoded_img_b = self.pad_encoded_img(encoded_img_b)
        byte_array = self.get_byte_array(padded_encoded_img_b)
        print(len(byte_array))
        output = open(output_path, 'wb')
        output.write(bytes(byte_array))

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