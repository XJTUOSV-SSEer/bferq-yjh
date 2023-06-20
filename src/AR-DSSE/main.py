import client
import server
import blockchain
import json
import pickle
import hmac
from web3 import Web3
import random
import sys


def test_scheme_honest(lb, ub, state_client, K_s, K_e, map_server, eth_contract, from_account):
    '''
    对方案进行测试，输出测试结果。这里server会诚实的进行搜索并返回结果

    Parameters:
    lb:范围的上界，如'13'
    ub:范围的下界，如'0'
    state_client：client的状态表
    K_s:
    K_e:
    map_server:
    eth_contract:合约对象
    from_account:server/client的账户



    Returns:
    none
    '''
    # client计算令牌ST
    ST, d, WSet = client.token_client(
        lb=lb,
        ub=ub,
        state_client=state_client,
        K_s=K_s
    )

    # server使用令牌进行搜索
    results = server.search_server(
        ST,
        map_server=map_server
    )

    # client对结果进行第一轮的验证
    flag_client = client.verify_client(
        results, d
    )

    print('client think it is ', flag_client)

    # 判断是否通过第一轮验证
    # 若未通过第一轮验证，需要命令区块链进行judge
    if not flag_client:
        # 计算l_w_list
        l_w_list = client.get_lw_list(
            state_client=state_client,
            WSet=WSet,
            K_s=K_s
        )

        # 验证
        flag_blockchain,gas = blockchain.verify(
            results=results,
            eth_contract=eth_contract,
            from_account=from_account,
            l_w_list=l_w_list
        )

        print('blockchain judge: the result is ', flag_blockchain)

        if flag_blockchain:
            print(client.decrypt_client(results=results, K_e=K_e))
    

    # 第一轮验证即通过，解密
    else:
        print(client.decrypt_client(results=results, K_e=K_e))
    
    return client.decrypt_client(results=results, K_e=K_e)









def test_scheme_cheat(lb, ub, state_client, K_s, K_e, map_server, eth_contract, from_account):
    '''
    对方案进行测试，输出测试结果。这里server是不诚实的，会随机生成若干个结果返回

    Parameters:
    lb:范围的上界，如'13'
    ub:范围的下界，如'0'
    state_client：client的状态表
    K_s:
    K_e:
    map_server:
    eth_contract:合约对象
    from_account:server/client的账户

    Returns:
    none
    '''
    # client计算令牌ST
    ST, d, WSet = client.token_client(
        lb=lb,
        ub=ub,
        state_client=state_client,
        K_s=K_s
    )


    # server随机生成若干个结果
    results = []
    for i in range(0,5):
        r=random.randint(-sys.maxsize-1,sys.maxsize)
        r=int(r).to_bytes(32,'big',signed=True)
        results.append(r)



    # client对结果进行第一轮的验证
    flag_client = client.verify_client(
        results, d
    )

    print('client think it is ', flag_client)

    # 判断是否通过第一轮验证
    # 若未通过第一轮验证，需要命令区块链进行judge
    if not flag_client:
        # 计算l_w_list
        l_w_list = client.get_lw_list(
            state_client=state_client,
            WSet=WSet,
            K_s=K_s
        )

        # 验证
        flag_blockchain,gas = blockchain.verify(
            results=results,
            eth_contract=eth_contract,
            from_account=from_account,
            l_w_list=l_w_list
        )

        print('blockchain judge: the result is ', flag_blockchain)

        # 解密
        if flag_blockchain:
            print(client.decrypt_client(results=results, K_e=K_e))
    
    # 第一轮验证即通过，解密
    else:
        print(client.decrypt_client(results=results, K_e=K_e))




def test_scheme_deny(lb, ub, state_client, K_s, K_e, map_server, eth_contract, from_account):
    '''
    对方案进行测试，输出测试结果。这里client是不诚实的，会拒绝接受server的结果

    Parameters:
    lb:范围的上界，如'13'
    ub:范围的下界，如'0'
    state_client：client的状态表
    K_s:
    K_e:
    map_server:
    eth_contract:合约对象
    from_account:server/client的账户

    Returns:
    none
    '''
    # client计算令牌ST
    ST, d, WSet = client.token_client(
        lb=lb,
        ub=ub,
        state_client=state_client,
        K_s=K_s
    )

    # server使用令牌进行搜索
    results = server.search_server(
        ST,
        map_server=map_server
    )

    # client对结果进行第一轮的验证后仍然拒绝接受
    flag_client = client.verify_client(
        results, d
    )
    flag_client=False

    print('client think it is ', flag_client)

    # 判断是否通过第一轮验证
    # 若未通过第一轮验证，需要命令区块链进行judge
    if not flag_client:
        # 计算l_w_list
        l_w_list = client.get_lw_list(
            state_client=state_client,
            WSet=WSet,
            K_s=K_s
        )

        # 验证
        flag_blockchain,gas = blockchain.verify(
            results=results,
            eth_contract=eth_contract,
            from_account=from_account,
            l_w_list=l_w_list
        )

        print('blockchain judge: the result is ', flag_blockchain)

        if flag_blockchain:
            print(client.decrypt_client(results=results, K_e=K_e))
    

    # 第一轮验证即通过，解密
    else:
        print(client.decrypt_client(results=results, K_e=K_e))










############################################ 以太坊账户、合约定义 ####################################
# 从当前目录下的abi.json文件读取abi
with open('./abi.json', 'r', encoding='utf8')as fp:
    contract_abi = json.load(fp)
# print(contract_abi)

# 创建一个Web3对象
w3 = Web3(Web3.WebsocketProvider("ws://127.0.0.1:8545"))

# client/server的账户from_account
from_account = w3.toChecksumAddress(input('输入server/client的eth账户:'))

# 创建合约对象eth_contract
eth_contract = w3.eth.contract(
    address=w3.toChecksumAddress(input('输入合约账户:')),
    abi=contract_abi
)


################################################# 数据准备 #############################################

# 从二进制文件中读取build用的字典数据 inverted_index
with open("data_10K.txt", 'rb') as f:  # 打开文件
    inverted_index = pickle.load(f)


# 生成K_e,K_s，使用hmac来生成
K_e = hmac.new(b'hong').digest()
K_s = hmac.new(b'guang').digest()
print('K_e=', K_e.hex())
print('K_s=', K_s.hex())


####################################### Build阶段 ###############################################

print('start build')
# 调用build_client函数，进行build
state_client, map_server, checklist = client.build_client(
    K_e=K_e,
    K_s=K_s,
    inverted_index=inverted_index
)
print('finish build')

# 定义下界和上界
lb = '1'
ub = '1'
# client计算令牌ST
ST, d, WSet = client.token_client(
    lb=lb,
    ub=ub,
    state_client=state_client,
    K_s=K_s
)
# server使用令牌进行搜索
results = server.search_server(
    ST,
    map_server=map_server
)


# client对结果进行第一轮的验证
flag = client.verify_client(
    results, d
)
print(flag)

# 解密
result_set = client.decrypt_client(results=results, K_e=K_e)
print(result_set)


# 输出三个字典容器
# print(state_client)
# print(map_server)
# print(checklist)


# 调用智能合约，将checklist发送至区块链
# 对checklist中每个l_w->digest pair，调用一次智能合约将其写入区块链
for l_w in checklist:
    tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
        "from": from_account,
        "gas": 3000000,
        "gasPrice": 1
    })


########################################### 加入新的 w-ind pair #############################################
print('start add')
# 新加入的元素
new_kw_files = {'0': ['0'], '1': ['7'], '4': ['2']}

# 将新元素加入
checklist = client.update_client(
    K_e=K_e,
    K_s=K_s,
    new_kw_files=new_kw_files,
    state_client=state_client,
    map_server=map_server
)

# 将新的checklist发送至区块链
for l_w in checklist:
    tx_hash = eth_contract.functions.set(l_w, checklist[l_w]).transact({
        "from": from_account,
        "gas": 3000000,
        "gasPrice": 1
    })
print('finish add')

# 输出三个字典容器
# print(state_client)
# print(map_server)
# print(checklist)


############################################### 进行范围搜索测试1 #################################################
print('start test case 1')
# 定义下界和上界
lb = '0'
ub = '4'

# 测试
dec_set=test_scheme_honest(
    lb=lb,
    ub=ub,
    state_client=state_client,
    K_s=K_s,
    K_e=K_e,
    map_server=map_server,
    eth_contract=eth_contract,
    from_account=from_account
)

# 与标准答案对比
with open ("v0_case1_dump.txt", 'rb') as f: #打开文件
    standard = pickle.load(f)
if dec_set==standard:
    print("equal to standard")

print('finish test case 1')

########################################### 运行范围测试2 ############################################
# 定义下界和上界
lb = '0'
ub = '999'

print('start test case 2')
# 测试
dec_set=test_scheme_honest(
    lb=lb,
    ub=ub,
    state_client=state_client,
    K_s=K_s,
    K_e=K_e,
    map_server=map_server,
    eth_contract=eth_contract,
    from_account=from_account
)

# 与标准答案对比
with open ("v0_case2_dump.txt", 'rb') as f: #打开文件
    standard = pickle.load(f)
if dec_set==standard:
    print("equal to standard")

print('finish test case 2')

########################################## 运行范围测试3，这里模拟服务器不进行search，而是随机选择数据返回#########
# 定义下界和上界
lb = '0'
ub = '999'

print('start test case 3')
test_scheme_cheat(
    lb=lb,
    ub=ub,
    state_client=state_client,
    K_s=K_s,
    K_e=K_e,
    map_server=map_server,
    eth_contract=eth_contract,
    from_account=from_account
)
print('finish test case 3')




########################################## 运行范围测试4，这里模拟client拒绝接受结果 #########
# 定义下界和上界
lb = '0'
ub = '999'

print('start test case 4')
test_scheme_deny(
    lb=lb,
    ub=ub,
    state_client=state_client,
    K_s=K_s,
    K_e=K_e,
    map_server=map_server,
    eth_contract=eth_contract,
    from_account=from_account
)
print('finish test case 4')