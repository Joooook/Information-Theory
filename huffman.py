import math
import time


def cmp(a):
    return a.weight
class HuffmanTreeNode(object):
    def __init__(self, byte, weight):
        self.weight = weight
        self.left_node = None
        self.right_node = None
        self.byte = byte#原码
        self.code = 0#编码
        self.code_length = 0

    def have_left_node(self):
        if self.left_node == None:
            return False
        return True

    def have_right_node(self):
        if self.right_node == None:
            return False
        return True

    def encode(self,code,length): #递归对结点编码
        if self.have_left_node():
            self.left_node.code = code << 1
            self.left_node.code_length = length
            self.left_node.encode(code<<1,length+1)
        if self.have_right_node():
            self.right_node.code=code << 1|1
            self.right_node.code_length=length
            self.right_node.encode(code << 1|1,length+1)
    def __str__(self):
        return str(self.byte)+' '+str(self.weight)

class HuffmanTree(object):
    def __init__(self):
        self.root = HuffmanTreeNode(0,0)
        self.code_list={}
        self.node_list=[]
        self.max_code_length=0
    def init(self,freq_list):
        self._init_node_list(freq_list)
        self._construct(self.node_list)
        return
    def _construct(self,node_list):#开始构造树
        if len(node_list)==2:
            self.root.left_node = node_list[0]
            self.root.right_node = node_list[1]
            return self.root
        return self._construct(self._combine(node_list))

    def encode(self):       #对构造好的树进行编码
        return self.root.encode(0,1)

    def _combine(self,node_list):                                         #合并节点
        combined_list=[]
        new_node=HuffmanTreeNode(0,0)
        new_node.left_node=node_list[-2]
        new_node.right_node=node_list[-1]
        new_node.weight=node_list[-2].weight+node_list[-1].weight
        i=0                                                         #index
        while new_node.weight<node_list[i].weight:
            combined_list.append(node_list[i])
            i+=1
        combined_list.append(new_node)
        combined_list+=node_list[i:-2]
        return combined_list


    def _init_node_list(self,freq_list):#生成结点为内容的列表，用于HUffman构造
        for i in range(len(freq_list)):
            if freq_list[i]!=0:
                self.node_list.append(HuffmanTreeNode(i,freq_list[i]))
        self.node_list.sort(key=cmp,reverse=True)


class Huffman(object):
    def __init__(self):
        self.path=None
        self.destination=None
        self.freq_list=[0]*0x100
        self.size=0
        self.dict=[]
        self.tree=HuffmanTree()
        self.min_len=100
        for i in range(0x100):
            self.dict.append([0,0])
    def _count_frequency(self): #统计字节出现频率
        with open(self.path, 'rb') as file:
            data = file.read()
        self.size = len(data)
        count_list=[0]*0x100
        for i in range(len(data)):
            count_list[data[i]]+=1
        for i in range(len(count_list)):
            self.freq_list[i]=count_list[i]/self.size
    def _init_dict(self,node):                #生成字典
        if node.have_left_node():
            self._init_dict(node.left_node)
        if node.have_right_node():
            self._init_dict(node.right_node)
        if not node.have_right_node() and not node.have_left_node():
            self.dict[node.byte]=[node.code,node.code_length]

    def encode(self):   #编码
        self._count_frequency()#统计frq
        self.tree.init(self.freq_list)#用频率统计表得到结点列表，用于huffman树的构建
        self.tree.encode()#huffman树构建结束要对树编码，构造过程是向上合并，encode过程是向下编码
        self._init_dict(self.tree.root)#生成表
        encoded_data=b'hzip'
        encoded_data+=  int.to_bytes(len(self.path.split('/')[-1]),1,'big')#文件名字节数
        encoded_data+=  self.path.split('/')[-1].encode()#文件名

        table=0#写入编码表
        count=0
        for i in range(0x100):
            if self.dict[i][1]>0:
                table=((table<<8|self.dict[i][1])<<self.dict[i][1])| self.dict[i][0]
                count+=8+self.dict[i][1]
            else:
                table = table << 8
                count+=8
        table=table<<(math.ceil(count/8)*8-count)#补位
        encoded_data += int.to_bytes(math.ceil(count/8), 2, 'big')  # 编码表长
        encoded_data += int.to_bytes(table,math.ceil(count/8), 'big')#编码表
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()
        with open(self.destination + '.hzip', 'wb') as out:
            out.write(encoded_data)
            endata=0
            count=0
            sum=0
            for i in data:
                sum+=1
                endata=(endata << self.dict[i][1])|self.dict[i][0]
                count+=self.dict[i][1]
                if count%8==0:
                    out.write(int.to_bytes(endata, count // 8, 'big'))
                    endata=0
                    count=0
            endata=endata<<(math.ceil(count/8)*8-count)#补位
            out.write(int.to_bytes(endata,math.ceil(count/8),'big'))
            out.close()


    def _table_to_dict(self,table,table_len):#解码时通过读入编码表转为字典
        count=0
        for i in range(0x100):
            code_len=table>>(table_len*8-8*(i+1)-count)  # 取data的前几位
            table=table^(code_len<<(table_len*8-8*(i+1)-count)) #删data的前几位
            count += code_len
            if code_len>0:
                code=table>>(table_len*8-8*(i+1)-count)
                table = table ^ (code << (table_len*8 - 8 * (i + 1) - count))
                self.dict[i]=[code,code_len]
                if code_len<self.min_len:
                    self.min_len=code_len
        return
    def _check(self,data,len):#对传入的进行查表还原，并返回剩下的字节
        byte=b''
        count=self.min_len
        sum=0
        for i in range(self.min_len,len+1):
            tmp=data>>(len-i)
            if [tmp,count] in self.dict:
                data=data^(tmp<<(len-i))
                byte+=int.to_bytes(self.dict.index([tmp,count]),1,'big')
                sum+=count
                count=0
                if len-sum<self.min_len:
                    break
            count+=1
        return byte,data,len-sum
    def decode(self):
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()

        if data[:4]!=b'hzip':#文件头校验
            raise Exception('错误的文件头')
        data=data[4:]

        name_len=data[0]#文件名长度
        name=data[1:name_len+1].decode(errors='replace')#文件名
        data=data[name_len+1:]

        table_len=int.from_bytes(data[:2],'big')#编码表长度
        table=int.from_bytes(data[2:table_len+2],'big')#读入头部表
        self._table_to_dict(table,table_len)#将头部表数据转换为dict
        data=data[table_len+2:]
        outbyte=b''
        with open(self.destination + name, 'wb') as out:
            count=0
            remain =0
            bit=1024
            for i in range(len(data)//bit):
                remain=remain<<(bit*8) | int.from_bytes(data[:bit],'big')
                count+=(bit*8)
                byte,remain,count=self._check(remain,count)
                outbyte+=byte
                data=data[bit:]
            byte, remain, count = self._check(remain, count)
            outbyte+=byte
            out.write(outbyte)

        return
if __name__ == '__main__':
    huffman=Huffman()
    huffman.path='2.hzip'
    huffman.destination='3'
    huffman.decode()
