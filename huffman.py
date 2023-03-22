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

    def construct(self,node_list):#开始构造树
        if len(node_list)==2:
            self.root.left_node = node_list[0]
            self.root.right_node = node_list[1]
            return self.root
        return self.construct(self._combine(node_list))

    def encode(self):       #对构造好的树进行编码
        return self.root.encode(0,0)

    def _init_code_list(self,node):                #获取编码表，内容为[code,code_length]
        if node.have_left_node():
            self._init_code_list(node.left_node)
        if node.have_right_node():
            self._init_code_list(node.right_node)
        if not node.have_right_node() and not node.have_left_node():
            if node.code_length>self.max_code_length:
                self.max_code_length=node.code_length
            self.code_list[node.byte]=[node.code,node.code_length]
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

    def init_node_list(self,freq_list):#生成结点为内容的列表，用于HUffman构造
        for i in range(len(freq_list)):
            if freq_list[i]!=0:
                self.node_list.append(HuffmanTreeNode(i,freq_list[i]))

class Huffman(object):
    def __init__(self):
        self.path=None
        self.destination=None
        self.freq_list=[0]*0x100
        self.size=0
        self.dict={}
        self.tree=HuffmanTree()
    def _count_frequency(self): #统计字节出现频率
        with open(self.path, 'rb') as file:
            data = file.read()
        self.size = len(data)
        count_list=[0]*0x100
        for i in range(len(data)):
            count_list[i]+=1
        for i in range(len(count_list)):
            self.freq_list[i]=count_list[i]/self.size

    def _init_dict(self):   #生成字典
        for i in range(0x100):
            if i in self.tree.code_list:
                self.dict[i]=self.tree.code_list[i]
            else:
                self.dict[i]=[0,0]
        return

    def encode(self):   #编码
        self._count_frequency()
        self.tree.init_node_list(self.freq_list)
        self.tree.construct(self.tree.node_list)
        self.tree.encode()
        self.tree._init_code_list(self.tree.root)
        self._init_dict()
        encoded_data=b''
        encoded_data+=int.to_bytes(self.tree.max_code_length,1,'big')#最长编码长度
        table=0#写入编码表
        for i in range(0x100):
            table=(table<<self.tree.max_code_length)| self.dict[i][0]
        encoded_data += int.to_bytes(table, 32*self.tree.max_code_length, 'big')#编码表
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()
        endata=0
        count=0
        for i in data:
            endata=(endata << self.dict[i][1])|self.dict[i][0]
            count+=self.dict[i][1]
        endata=endata<<((count//8+1)*8-count)#补位
        encoded_data+=int.to_bytes(endata,count//8+1,'big')

        with open(self.destination + '.hzip', 'wb') as out:
            out.write(encoded_data)


    def _table_to_dict(self,table,len):#解码时通过读入编码表转为字典
        for i in range(0x100):
            if i in self.tree.code_list:
                self.dict[i]=self.tree.code_list[i]
            else:
                self.dict[i]=[0,0]
        return
    def decode(self):
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()
        max_len=data[0]#最大编码长度
        table=data[1:32*max_len+1]
        self._table_to_dict(table,max_len)
        encoded_origin_data=#去除文件头的data
        decoded_data=0
        for i in data:

        with open(self.destination + '.hzip', 'wb') as out:
            out.write(decoded_data)
        return

if __name__ == '__main__':
    huffman=Huffman()
    huffman.path='1'
    huffman.destination='2'
    huffman.encode()
