import copy
from pydoc import cli
import client
import server
import blockchain
import json
import pickle
import hmac
from web3 import Web3
import random
import sys
import time


def experiment_build(dataset):
    '''
    对不同大小的数据集测试其build时间

    Parameters:
    dataset: 数据集的路径

    Returns:
    delay: 花费的时间
    '''
    # 从二进制文件中读取build用的字典数据 inverted_index
    with open(dataset, 'rb') as f:  # 打开文件
        inverted_index = pickle.load(f)


    t1=time.time()
    
    # 调用build_client函数，进行build
    state_client, map_server, checklist,MSK_0,map_r = client.build_client(
        K_e=K_e,
        K_s=K_s,
        inverted_index=inverted_index
    )

    t2=time.time()

    return t2-t1


def experiment_add(dataset):
    '''
    在已经用一个10K数据集build的前提下，测试add不同数据集的时间

    Parameters:
    dataset: 数据集的路径

    Returns:
    delay: 花费的时间
    '''

    # 读取数据
    with open(dataset, 'rb') as f:  # 打开文件
        new_kw_files = pickle.load(f)

    t1=time.time()
    map_del={}
    checklist=client.update_client(K_e,K_s,new_kw_files,state_client,map_server,'add',MSK_0,map_r,map_del)
    t2=time.time()

    return t2-t1


def experiment_token(lb,ub):
    '''
    给定上下限，获取用户计算令牌的时间和令牌数量

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:用户计算令牌的时间
    n:令牌数量
    '''
    lb=str(lb)
    ub=str(ub)

    t1=time.time()
    ST,d,Wset=client.token_client(lb,ub,state_client,K_s,MSK_0,map_del={})
    t2=time.time()

    return t2-t1,len(Wset)

    
def experiment_search(lb,ub):
    '''
    给定上下限，获取云服务器搜索的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:服务器搜索的时间
    '''
    lb=str(lb)
    ub=str(ub)
    ST,d,Wset=client.token_client(lb,ub,state_client,K_s,MSK_0,map_del={})

    t1=time.time()
    results=server.search_server(ST,map_server)
    t2=time.time()
    return t2-t1


def experiment_verify(lb,ub):
    '''
    给定上下限，获取用户验证的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:用户第一轮验证的时间
    '''
    lb=str(lb)
    ub=str(ub)
    ST,d,Wset=client.token_client(lb,ub,state_client,K_s,MSK_0,map_del={})
    results=server.search_server(ST,map_server)

    t1=time.time()
    flag=client.verify_client(results,d)
    t2=time.time()
    print(flag)
    return t2-t1


def experiment_decrypt(lb,ub):
    '''
    给定上下限，获取用户解密的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:用户解密的时间
    '''
    lb=str(lb)
    ub=str(ub)
    ST,d,Wset=client.token_client(lb,ub,state_client,K_s,MSK_0,map_del={})
    results=server.search_server(ST,map_server)

    t1=time.time()
    msg=client.decrypt_client(results,K_e)
    t2=time.time()
    return t2-t1



def experiment_judge(lb,ub):
    '''
    给定上下限，获取区块链第二轮验证的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:区块链第二轮验证的时间
    gas: 花费的gas
    '''
    lb=str(lb)
    ub=str(ub)
    ST,d,Wset=client.token_client(lb,ub,state_client,K_s,MSK_0,map_del={})
    results=server.search_server(ST,map_server)
    l_w_list=client.get_lw_list(state_client,Wset,K_s)

    t1=time.time()
    flag,gas=blockchain.verify(results,eth_contract,from_account,l_w_list)
    t2=time.time()
    print(flag)
    return t2-t1,gas



def experiment_del(dataset):
    '''
    在已经用一个10K数据集build的前提下，先add不同的数据集，然后测试del这些数据集的时间

    要格外小心删除的数据大于限定的最大值d（尤其是靠近root的结点）

    同时，务必保证add的数据与之前已有的数据不重复，否则刺穿的时候会出问题，搜索的啥时候会把同一个w多个ind都刺穿，导致
    和digest对不上

    Parameters:
    dataset: 数据集的路径

    Returns:
    delay1: 删除的时间
    delay2: 之后搜索的时间
    '''

    # 先用10K数据集进行build，并设置对应的checklist
    with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
            inverted_index = pickle.load(f)
    state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)
    # for l_w in checklist:
    #     tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
    #         "from": from_account,
    #         "gas": 3000000,
    #         "gasPrice": 0
    #     })



    # 读取数据
    with open(dataset, 'rb') as f:  # 打开文件
        new_kw_files = pickle.load(f)

    # 注意 new_kw_files 要深拷贝两份分别用于update和add!!!!!!!否则dict类型的变量会在add之后发生改变
    new_kw_files1=copy.deepcopy(new_kw_files)
    new_kw_files2=copy.deepcopy(new_kw_files)

    # new_kw_files={'0':['1','2'],'1':['2','3']}

    map_del={}

    # 先add这些数据
    checklist=client.update_client(K_e,K_s,new_kw_files1,state_client,map_server,'add',MSK_0,map_r,map_del)
    ST,d,Wset=client.token_client('0','1000',state_client,K_s,MSK_0,map_del)
    results=server.search_server(ST,map_server)
    # print(client.decrypt_client(results,K_e))
    


    # for l_w in checklist:
    #     tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
    #         "from": from_account,
    #         "gas": 3000000,
    #         "gasPrice": 0
    # })

    # delete
    t1=time.time()
    checklist=client.update_client(K_e,K_s,new_kw_files2,state_client,map_server,'del',MSK_0,map_r,map_del)
    t2=time.time()
    delay1=t2-t1
    # for l_w in checklist:
    #     tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
    #         "from": from_account,
    #         "gas": 3000000,
    #         "gasPrice": 0
    # })



    # 范围查询
    ST,d,Wset=client.token_client('0','1000',state_client,K_s,MSK_0,map_del)
    t1=time.time()
    results=server.search_server(ST,map_server)
    t2=time.time()
    delay2=t2-t1
    l_w_list=client.get_lw_list(state_client,Wset,K_s)

    flag1=client.verify_client(results,d)
    # print(client.decrypt_client(results,K_e))
    # flag2,gas=blockchain.verify(results,eth_contract,from_account,l_w_list)
    print(flag1)

    # if not (flag1 and flag2):
    #     print('wrong answer')

    return delay1,delay2








############################################ 以太坊账户、合约定义 ####################################
# 从当前目录下的abi.json文件读取abi
with open('./abi.json', 'r', encoding='utf8')as fp:
    contract_abi = json.load(fp)
# print(contract_abi)

# 创建一个Web3对象
w3 = Web3(Web3.WebsocketProvider("ws://127.0.0.1:8545"))

# client/server的账户from_account
from_account = w3.toChecksumAddress('0x6898ED602b8a883f6Bc9bC22F9464AA25d29a59E')


# 创建合约对象eth_contract
eth_contract = w3.eth.contract(
    address=w3.toChecksumAddress('0x33E78cE26281b0e385e3ffD1bEAaBD5E1FCe067A'),
    abi=contract_abi
)

################################################# 数据准备 #############################################
# 生成K_e,K_s，使用hmac来生成
K_e = hmac.new(b'hong').digest()
K_s = hmac.new(b'guang').digest()
print('K_e=', K_e.hex())
print('K_s=', K_s.hex())


############################### 测试build的速度 ###############################
# 每种数据集进行五次取平均值

# 2K数据集
# t=0
# for i in range(5):
#     t=t+experiment_build('../data/data_2K.txt')

# print('2K dataset:',t/5)

# 4K数据集
# t=0
# for i in range(5):
#     t=t+experiment_build('../data/data_4K.txt')

# print('4K dataset:',t/5)

# 6K数据集
# t=0
# for i in range(5):
#     t=t+experiment_build('../data/data_6K.txt')

# print('6K dataset:',t/5)

# 8K数据集
# t=0
# for i in range(5):
#     t=t+experiment_build('../data/data_8K.txt')

# print('8K dataset:',t/5)

# 10K数据集
# t=0
# for i in range(5):
#     t=t+experiment_build('../data/data_10K.txt')

# print('10K dataset:',t/5)




#################################### 测试插入数据的速度 #######################

# 先用10K数据集进行build
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)

# 400数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('../data/data_400.txt')
# print('400:',t/5)

# 800数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('../data/data_800.txt')
# print('800:',t/5)

# 1200数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('../data/data_1200.txt')
# print('1200:',t/5)

# 1600数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('../data/data_1600.txt')
# print('1600:',t/5)

# 2000数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('../data/data_2000.txt')
# print('2000:',t/5)



############################# 测试计算ST的数量和时间 ##############################

# 先用10K数据集进行build
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)


# 0-200范围
# total_t=0
# for i in range(5):
#     t,n=experiment_token(0,200)
#     total_t=total_t+t
# print('0-200:',total_t/5,n)

# 0-400范围
# total_t=0
# for i in range(5):
#     t,n=experiment_token(0,400)
#     total_t=total_t+t
# print('0-400:',total_t/5,n)

# 0-600范围
# total_t=0
# for i in range(5):
#     t,n=experiment_token(0,600)
#     total_t=total_t+t
# print('0-600:',total_t/5,n)

# 0-800范围
# total_t=0
# for i in range(5):
#     t,n=experiment_token(0,800)
#     total_t=total_t+t
# print('0-800:',total_t/5,n)

# 0-1000范围
# total_t=0
# for i in range(5):
#     t,n=experiment_token(0,1000)
#     total_t=total_t+t
# print('0-1000:',total_t/5,n)





############################ 测试云服务器搜索时间 #################################

# 先用10K数据集进行build
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)


# [0,200]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,200)
# print('0-200:',t/5)

# [0,400]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,400)
# print('0-400:',t/5)

# [0,600]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,600)
# print('0-600:',t/5)

# [0,800]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,800)
# print('0-800:',t/5)

# [0,1000]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,1000)
# print('0-1000:',t/5)




########################## 测试第一轮验证的速度 ##############################

# 先用10K数据集进行build
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)


# 0-200
# t=0
# for i in range(5):
#     t=t+experiment_verify(0,200)
# print('0-200:',t/5)

# 0-400
# t=0
# for i in range(5):
#     t=t+experiment_verify(0,400)
# print('0-400:',t/5)

# 0-600
# t=0
# for i in range(5):
#     t=t+experiment_verify(0,600)
# print('0-600:',t/5)

# 0-800
# t=0
# for i in range(5):
#     t=t+experiment_verify(0,800)
# print('0-800:',t/5)

# 0-1000
# t=0
# for i in range(5):
#     t=t+experiment_verify(0,1000)
# print('0-1000:',t/5)





############################## 测试用户的解密时间 ##################################
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)

# 0-200
# t=0
# for i in range(5):
#     t=t+experiment_decrypt(0,200)
# print('0-200:',t/5)

# 0-400
# t=0
# for i in range(5):
#     t=t+experiment_decrypt(0,400)
# print('0-400:',t/5)

# 0-600
# t=0
# for i in range(5):
#     t=t+experiment_decrypt(0,600)
# print('0-600:',t/5)

# 0-800
# t=0
# for i in range(5):
#     t=t+experiment_decrypt(0,800)
# print('0-800:',t/5)

# 0-1000
# t=0
# for i in range(5):
#     t=t+experiment_decrypt(0,1000)
# print('0-1000:',t/5)





#################################### 测试区块链验证时间和gas ###############################
# 先用10K数据集进行build，并设置对应的checklist
# with open('../data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# state_client,map_server,checklist,MSK_0,map_r=client.build_client(K_e,K_s,inverted_index)
# for l_w in checklist:
#     tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
#         "from": from_account,
#         "gas": 3000000,
#         "gasPrice": 0
#     })



# 0-200
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,200)
#     t=t+delay
#     g=g+gas
# print('0-200:',t/5,g/5)

# 0-400
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,400)
#     t=t+delay
#     g=g+gas
# print('0-400:',t/5,g/5)

# 0-600
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,600)
#     t=t+delay
#     g=g+gas
# print('0-600:',t/5,g/5)

# 0-800
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,800)
#     t=t+delay
#     g=g+gas
# print('0-800:',t/5,g/5)

# 0-1000
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,1000)
#     t=t+delay
#     g=g+gas
# print('0-1000:',t/5,g/5)





################################ 测试删除不同数据集的时间，以及删除后搜索的时间 ###############################

# 用于测试del的数据


# 1K数据集
t1=0
t2=0
for i in range(5):
    delay1,delay2=experiment_del("../data/data_del_1K.txt")
    t1=t1+delay1
    t2=t2+delay2
print('1K:',t1/5,t2/5)

# 2K
t1=0
t2=0
for i in range(5):
    delay1,delay2=experiment_del("../data/data_del_2K.txt")
    t1=t1+delay1
    t2=t2+delay2
print('1K:',t1/5,t2/5)


# 3K
t1=0
t2=0
for i in range(5):
    delay1,delay2=experiment_del("../data/data_del_3K.txt")
    t1=t1+delay1
    t2=t2+delay2
print('1K:',t1/5,t2/5)


# 4K
t1=0
t2=0
for i in range(5):
    delay1,delay2=experiment_del("../data/data_del_4K.txt")
    t1=t1+delay1
    t2=t2+delay2
print('1K:',t1/5,t2/5)


# 5K
t1=0
t2=0
for i in range(5):
    delay1,delay2=experiment_del("../data/data_del_5K.txt")
    t1=t1+delay1
    t2=t2+delay2
print('1K:',t1/5,t2/5)