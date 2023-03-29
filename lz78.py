import os
import time
from tqdm import tqdm
import math
class lz78(object):
    def __init__(self):
        self.path = ''
        self.destination = ''
        self.freq_list = [0] * 0x100
        self.size = 0
        self.dict = {}
        self.inv_dict = {}
        self.in_filename = ''
        self.out_filename = ''  # output_file_name
        self.show_info = True
        self.start_time = 0
        self.end_time = 0
        self.max_len=0
    def encode(self):
        self.path='jp.docx'
        with open(self.path, 'rb') as file:  # 写入文件数据
            data = file.read()
        while os.path.exists(self.destination + self.out_filename):
            op = input(
                "\033[4;33mThe file " + self.out_filename + " have existed, would you like to overwrite?[y/N]\033[0m")
            if op == 'y' or op == 'Y':
                break
            elif op == 'n' or op == 'N':
                if '.' in self.out_filename:
                    self.out_filename = self.out_filename.split('.')[0] + '_.' + self.out_filename.split('.')[1]
                else:
                    self.out_filename += '_'
            else:
                print("\033[5;33mPlease input [y/N]!!!\033[0m")
        self.start_time = time.time()
        if self.show_info:
            print(
                'Input filename: ' + self.path + ', ' + 'Output file: ' + self.destination + self.out_filename + ', ' + 'File Size: ' + str(
                    self.size) + 'bytes')
        with open(self.destination + self.out_filename+'tmp', 'wb') as out:
            tmp=b''
            count=0
            for i in tqdm(range(len(data))):
                tmp+=data[i:i+1]
                if tmp not in self.dict.keys():
                    count+=1
                    index=count
                    if len(tmp)==1:
                        code=int.from_bytes(tmp, 'big')
                        front_index=0
                    else:
                        code=tmp[-1]
                        front_index=self.dict[tmp[:-1]][0]
                    length = len(bin(front_index)[2:])
                    if length > self.max_len:
                        self.max_len = length
                    self.dict[tmp] = [index,front_index,code]#index的长度
                    tmp=b''
            count=0
            endata=0
            for i in tqdm(list(self.dict.values())):
                endata=(endata<<self.max_len | i[1])<<8 | i[2]
                count+=(self.max_len+8)
                if count % 8 == 0:
                    out.write(int.to_bytes(endata, count // 8, 'big'))
                    endata = 0
                    count=0
            endata = endata << (math.ceil(count / 8) * 8 - count)  # 补位
            out.write(int.to_bytes(endata, math.ceil(count / 8), 'big'))
            out.close()
        self.end_time = time.time()
        if self.show_info:
            print('Cost ' + f'%.4f' % (self.end_time - self.start_time) + ' secs,' + 'encode ' + str(
                self.size) + ' bytes, ' + 'speed: ' + f'%.4f' % (
                          self.size / (self.end_time - self.start_time)) + ' byte/s, ' + 'ratio: ' + f'%.2f' % (
                              os.path.getsize(self.destination + self.out_filename) / os.path.getsize(
                          self.path) * 100) + '%')
if __name__ == '__main__':
    lz=lz78()
    lz.encode()