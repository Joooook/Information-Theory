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
        return self.root.encode(0,0)

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
        for i in combined_list:
            print(i,end=' ')
        print()
        return combined_list

    def _init_node_list(self,freq_list):#生成结点为内容的列表，用于HUffman构造
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
            count_list[data[i]]+=1
        for i in range(len(count_list)):
            self.freq_list[i]=count_list[i]/self.size
    def _init_dict(self,node):                #生成字典
        if node.have_left_node():
            self._init_dict(node.left_node)
        if node.have_right_node():
            self._init_dict(node.right_node)
        if not node.have_right_node() and not node.have_left_node():
            if node.code_length>self.max_code_length:
                self.max_code_length=node.code_length
            self.dict[node.byte]=[node.code,node.code_length]

    def encode(self):   #编码
        self._count_frequency()#统计frq
        self.tree.init(self.freq_list)#用频率统计表得到结点列表，用于huffman树的构建
        self.tree.encode()#huffman树构建结束要对树编码，构造过程是向上合并，encode过程是向下编码
        self._init_dict(self.tree.root)#生成表
        encoded_data=b'hzip'
        encoded_data+=  int.to_bytes(len(self.path.split('/')[-1]),1,'big')#文件名字节数
        encoded_data+=  self.path.split('/')[-1].encode()#文件名
        encoded_data+=  int.to_bytes(self.tree.max_code_length,1,'big')#最长编码长度
        table=0#写入编码表
        for i in range(0x100):
            if i in list(self.dict.keys()):
                table=((table<<1|1)<<self.tree.max_code_length)| self.dict[i][0]
            else:
                table = table << 1
        print(bin(table))
        encoded_data += int.to_bytes(table, 32*self.tree.max_code_length, 'big')#编码表
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()
        endata=0
        count=0
        for i in data:
            endata=(endata << self.dict[i][1])|self.dict[i][0]
            count+=self.dict[i][1]
        print(hex(endata))
        endata=endata<<((count//8+1)*8-count)#补位
        print(self.dict)
        print(hex(endata))
        print(count)
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
    def _get_byte(self,code):#给编码，从字典中获取原字节
        vals=list(self.dict.values())
        keys=list(self.dict.keys())
        for i in range(vals):
            if vals[i]==code:
                return int.from_bytes(keys[i],'big')
        return None
    def _table_to_dict(self,table,len):
        t=int.from_bytes(table, 'big')
        while

    def decode(self):
        with open(self.path, 'rb') as file:#写入文件数据
            data = file.read()

        if data[:4]!=b'hzip':#文件头校验
            raise Exception('错误的文件头')
        data=data[4:]

        name_len=data[0]#文件名长度
        name=data[1:name_len+1].decode(errors='replace')#文件名
        data=data[name_len+1:]

        max_len=data[0]#最大编码长度
        table=data[1:32*max_len+1]#读入头部表
        self._table_to_dict(table,max_len)#将头部表数据转换为dict,未完成！！

        encoded_origin_data= int.from_bytes(data[32*max_len+1:],'big')  #去除文件头的data
        encoded_origin_data_length=len(data[32*max_len+1:])*8   #2进制长度
        decoded_data=b''
        i=0
        count=1
        while i<encoded_origin_data_length:
            tmp=encoded_origin_data>>(encoded_origin_data_length-count-1)#取data的前几位
            if [tmp,count] in self.dict.values():       #如果dict里面有，则用get_byte查询键，返回
                decoded_data+=self._get_byte([tmp,count])
                encoded_origin_data=(tmp<<(encoded_origin_data_length-count-1))^encoded_origin_data   #删除已经替换完的值
                count=0                             #count是表示当前的tmp长度，因为长度和值才能一起对应于一个键
            i+=1
            count+=1
        with open(self.destination + name, 'wb') as out:
            out.write(decoded_data)
        return

if __name__ == '__main__':
    huffman=Huffman()
    huffman.path='1'
    huffman.destination='2'
    huffman.encode()
