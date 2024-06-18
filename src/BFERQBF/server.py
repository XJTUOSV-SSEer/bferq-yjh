from ctypes import c_byte, wstring_at
from web3 import Web3
import random
import sys
import hmac
from Crypto.Cipher import AES
import copy
import SPE

def search_server(ST,map_server):
    '''
    server端根据搜索令牌查找得到密文

    Parameters:
    ST：搜索令牌，一个list，包含若干个[K_w,gamma_add_0,msk_c,gamma_del_0]
    map_server：server端的储存容器，将addr映射到[P,V]

    Returns:
    results：一个list，储存搜索得到的密文

    '''
    results=[]
    
    # 遍历ST中所有的[K_w,gamma_add_0,msk_c,gamma_del_0]
    for i in ST:
        # 得到K_w,gamma_0,msk_c,gamma_del_0
        K_w=i[0]
        gamma_add_0=i[1]
        msk_c=i[2]
        gamma_del_0=i[3]

        # 创建一个AES对象，密钥是K_w，即算法中的PRF G
        PRF_G=AES.new(key=K_w,mode=AES.MODE_ECB)



        # 找到所有psk并计算SK，通过server上的穿刺链
        # 计算穿刺链的首地址addr_del_0
        addr_0=PRF_G.encrypt(gamma_del_0)
        # 初始化SK
        SK=[msk_c]


        # 遍历找到所有psk来构造SK
        addr=addr_0
        while addr in map_server:
            # 找到pos，psk，t
            pos,psk,t=map_server[addr]

            # 将psk加入SK
            SK.append(psk)

            # 计算下一个位置的gamma
            gamma_next=bytes(a^b for a,b in zip(pos,addr))

            # 计算下一个位置addr
            addr=PRF_G.encrypt(gamma_next)



        # 遍历找到链上所有的ct，并使用SPE进行解密
        addr_0=PRF_G.encrypt(gamma_add_0) 
        addr=addr_0
        while addr in map_server:
            # 找到pos和ct,t
            pos,ct,t=map_server[addr]

            # 对val进行穿刺解密
            val=SPE.Dec(SK,ct,t)            

            # 若解密结果不为空，将密文val加入结果
            if val is not None:
                results.append(val)

            # 计算下一个位置的gamma
            gamma_next=bytes(a^b for a,b in zip(pos,addr))
            
            # 计算下一个位置addr
            addr=PRF_G.encrypt(gamma_next)
    return results




