import os
import time
from tqdm import tqdm
import math
import argparse
class lz78(object):
    def __init__(self):
        self.path = ''
        self.destination = ''
        self.freq_list = [0] * 0x100
        self.size = 0
        self.dict = {}
        self.in_filename = ''
        self.out_filename = ''  # output_file_name
        self.show_info = True
        self.start_time = 0
        self.end_time = 0
        self.max_len=0
        self.remain_len=0
    def _init_dict(self):
        with open(self.path, 'rb') as file:  # 写入文件数据
            data = file.read()
        tmp = b''
        count = 1
        for i in tqdm(range(len(data))):
            tmp += data[i:i + 1]
            if tmp not in self.dict.keys():
                index = count
                if len(tmp) == 1:
                    code = int.from_bytes(tmp, 'big')
                    front_index = 0
                else:
                    code = tmp[-1]
                    front_index = self.dict[tmp[:-1]][0]
                length = len(bin(front_index)[2:])
                if length > self.max_len:
                    self.max_len = length
                self.dict[tmp] = [index, front_index, code]  # index的长度
                tmp = b''
                count += 1
        self.remain_len=len(tmp)
        return tmp
    def _write_dict(self,out):
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
    def _show_start_info(self):
        if self.show_info:
            print(
                'Input filename: ' + self.path + ', ' + 'Output file: ' + self.destination + self.out_filename + ', ' + 'File Size: ' + str(
                    self.size) + 'bytes')
    def _show_end_info(self):
        if self.show_info:
            print('Cost ' + f'%.4f' % (self.end_time - self.start_time) + ' secs, ' + 'Process ' + str(
                self.size) + ' bytes, ' + 'Speed: ' + f'%.4f' % (
                          self.size / (self.end_time - self.start_time)) + ' byte/s, ' + 'Ratio: ' + f'%.2f' % (
                              os.path.getsize(self.destination + self.out_filename) / os.path.getsize(
                          self.path) * 100) + '%')
    def _file_existed_check(self):
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
    def _write_header(self,out):
        header = b'lz78'
        header += int.to_bytes(len(self.in_filename), 1, 'big')  # 文件名字节数
        header += self.in_filename.encode()  # 文件名
        header += int.to_bytes(self.max_len, 1, 'big')  # frontindex的二进制长度
        header += int.to_bytes(self.remain_len, 1, 'big') #剩余未编码字节长度
        out.write(header)
        return
    def _read_header(self):
        with open(self.path, 'rb') as file:  # 写入文件数据
            data = file.read()
            file.close()
        if data[:4] != b'lz78':  # 文件头校验
            raise Exception('错误的文件头')
        data = data[4:]
        name_len = data[0]  # 文件名长度
        self.out_filename = data[1:name_len + 1].decode(errors='replace')  # 文件名
        data = data[name_len + 1:]
        self.max_len = data[0]# frontindex占多少位
        self.remain_len= data[1]
        remain=data[-self.remain_len:]
        data=data[2:-self.remain_len]
        self.size = len(data)
        return data,remain
    def _parse(self, data, word_num):  # 对传入的进行还原表并译码,length是word的数量
        byte=b''
        for i in range(word_num):
            index=len(self.dict.keys())+1
            word= data >>((word_num - i - 1) * (8 + self.max_len))
            data = data ^ (word << ((word_num - i - 1) * (8 + self.max_len)))
            front_index=word>>8
            code = int.to_bytes(word&0xFF, 1, 'big')
            if front_index!=0:
                tmp=list(self.dict.keys())[front_index-1]+code
            else:
                tmp =code
            self.dict[tmp] = [index, front_index, code]
            byte+=tmp
        return byte
    def _decode_file(self,data,out):
        count = 0
        tmp=0
        word_len=8+self.max_len
        word_num=self.size*8//word_len
        supbit_len=self.size*8-(self.size*8//word_len)*word_len #补位长度
        for i in tqdm(range(self.size // word_len)):
            byte= self._parse(int.from_bytes(data[word_len * i:word_len * (i + 1)], 'big'), 8)
            out.write(byte)
        byte= self._parse(int.from_bytes(data[word_len*(self.size // word_len):],'big')>>supbit_len, word_num%8)
        out.write(byte)
    def encode(self):
        self._file_existed_check()
        self._show_start_info()
        self.start_time = time.time()
        remain=self._init_dict()
        with open(self.destination + self.out_filename , 'wb') as out:
            self._write_header(out)
            self._write_dict(out)
            out.write(remain)
            out.close()
        self.end_time = time.time()
        self._show_end_info()
    def decode(self):
        self.start_time = time.time()
        data,remain=self._read_header()
        self._show_start_info()
        self._file_existed_check()
        with open(self.destination + self.out_filename, 'wb') as out:
            self._decode_file(data,out)
            out.write(remain)
        self.end_time = time.time()
        self._show_end_info()
if __name__ == '__main__':
    lz=lz78()
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='Input the path of the file to be encoded/decoded')
    parser.add_argument('-d', '--destination', type=str, required=False, default='',
                        help='Input the dir path of the file to be output')
    parser.add_argument('-m', '--mode', type=str, required=True, choices=['encode', 'decode'],
                        help='Choose encode/decode mode')
    parser.add_argument('-l', '--less', action='store_true', required=False, default=False,
                        help='Hide details of the process')
    opt = parser.parse_args()
    if not os.path.exists(opt.path):
        raise FileNotFoundError('Error: No such file')
    if '\\' in opt.path:
        lz.in_filename = opt.path.split('\\')[-1]
    else:
        lz.in_filename = opt.path
    lz.path = opt.path
    lz.destination = opt.destination
    lz.show_info = not opt.less
    if opt.mode == 'encode':
        if '.' in lz.in_filename:
            lz.out_filename = lz.in_filename.split('.')[0] + '.lzip'
        else:
            lz.out_filename = lz.in_filename + '.lzip'
        lz.encode()
    elif opt.mode == 'decode':
        lz.decode()
    print(opt.mode + ' finished. Output: ' + lz.out_filename)
