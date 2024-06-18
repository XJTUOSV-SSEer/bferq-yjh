import pickle

def transform_data():
    '''
    读取'./dataset_10K'目录下所有的文件，这些文件名为关键字的值，文件内容为倒排索引

    将倒排索引转换为普通字符串的形式并用pickle持久化储存为'./data_10K.txt'

    示例：如文件1包含数据23,34；文件2包含数据56,78。那么得到一个普通的倒排索引{'1':['23','34'],'2':['56','78']}

    Parameters:
    none

    Returns:
    none
    '''

    # 普通的倒排索引
    inverted_index={}

    # 循环1000次读取文件
    for i in range(1,1001):
        # 计算文件名
        filename='./dataset_10K/'+str(i)

        # 打开该文件
        with open(filename,'r',encoding='utf-8') as f:
            # 读取所有数据
            s=f.read()
        
        # 按照','将数字分开得到一个list
        l=s.split(',')

        # 加入倒排索引
        inverted_index[str(i)]=l

    # 将倒排索引写入到二进制文件中
    with open ("data_10K.txt", 'wb') as f: #打开文件
        pickle.dump(inverted_index, f)


if __name__=='__main__':
    transform_data()

    # 测试
    with open ("data_10K.txt", 'rb') as f: #打开文件
        dict=pickle.load(f)
    
    print(dict['999'])
    print(dict['1000'])
