from Crypto.Cipher import AES
import hmac

'''
提供SPE（对称可穿刺加密）的KeyGen,Enc,Pun,Dec四个函数
穿刺PRF使用GGM-Tree实例化
'''


def bin2str(data):
    '''
    将二进制形式的数据转换为逻辑上相同的01串。

    示例：原始数据的二进制形式为0b00000101，那么返回字符串'00000101'

    Parameters:
    data:一个bytes数组

    Returns：
    s: 对应的01字符串    
    '''
    # 获取data的字节数和bit数
    bytes_num = len(data)
    bits_num = bytes_num*8

    # 将data转换为二进制字符串
    s = ''
    for i in range(bytes_num):
        # 将当前字节转换为int
        v = int(data[i])

        # int转换为二进制字符串
        v = bin(v).replace('0b', '')

        # 若字符串不满8位，补为8位
        v = v.rjust(8, '0')

        # 将其加入结果中
        s = s+v

    return s


def generator(seed, flag):
    '''
    计算G(seed,flag)。其中seed是PRG的种子，flag是0或1。

    Parameters:
    seed：128位的bytes
    flag：0或1

    Returns：
    PRG结果的左半部分或右半部分，128位
    '''
    # 使用2个AES来实现这个PRG，一个生成左半部分，一个生成右半部分
    prg_l = AES.new(key='PRG_L'.zfill(16).encode('utf-8'), mode=AES.MODE_ECB)
    prg_r = AES.new(key='PRG_R'.zfill(16).encode('utf-8'), mode=AES.MODE_ECB)

    # 判断需要的是哪半部分
    if flag == 0:
        return prg_l.encrypt(seed.zfill(16))
    elif flag == 1:
        return prg_r.encrypt(seed.zfill(16))


def PPRF_punc(t, sk, sec_parameter=128):
    '''
    穿刺PRF对t进行穿刺，返回穿刺密钥psk

    Parameters:
    t:tag，一个byres数组
    sk：穿刺时对应的sk。sk_i对应psk_i+1
    sec_parameter：安全参数

    Returns:
    psk：穿刺密钥，一个list容器，其中包含2个元素。第一个元素储存sk，第二个list储存所有可达的前缀路径    
    '''
    # 将t转换为01字符串
    t = bin2str(t)

    # 找到从叶结点到root的路径对应的所有兄弟结点
    # 具体方法是末尾取反得到一个元素，然后向右移位重复此过程
    psk = []
    for i in range(len(t)):
        if t[-1] == '0':
            s = t[0:len(t)-1]+'1'
        else:
            s = t[0:len(t)-1]+'0'

        # 更新list
        psk.append(s)

        # 更新t
        t = t[0:len(t)-1]

    psk = [sk, psk]
    return psk


def PPRF_cal(sk, t, sec_parameter=128):
    '''
    计算F(sk,t)

    Parameters:
    sk:PRF的key，128位的bytes数组
    t：PRF的x值，一个128位的bytes数组
    sec_parameter：安全参数

    Returns:
    val：计算结果，默认为128位

    '''
    # 将t从128位的bytes数组转换为128字节的01型字符串
    # 如：数据为0b0001，转换为'0001'
    # t = bin2str(t)

    # 最后的结果，初始为sk
    val = sk

    # 通过GGM-tree的公式计算PRF的值
    # for i in range(len(t)):
    #     # 该位是0还是1
    #     flag = t[-i-1]
    #     flag = int(flag)
    #     val = generator(val, flag)

    # 用AES计算PRF的值
    val=AES.new(key=sk,mode=AES.MODE_ECB).encrypt(t)

    return val


def PPRF_eval(psk, t):
    '''
    给定穿刺密钥psk，计算t的PRF值。若t被穿刺过，则返回none
    Parameters:
    psk：一个list，第一个元素包含sk，第二个元素也是一个list，包含允许计算的前缀
    t：tag

    Returns:
    val：计算结果或none。128位bytes

    '''
    # 得到sk和允许计算的前缀列表allow
    sk = psk[0]
    allow = psk[1]

    # 将t转换为01字符串
    s_t = bin2str(t)

    # 判断是否被穿刺过
    for s in allow:
        # 判断s是否为t的前缀。若是，计算PRF值并返回
        if s_t[0:len(s)] == s:
            return PPRF_cal(sk, t)

    # t被穿刺过，无法计算，返回none
    return


def KeyGen(sec_parameter=128, d=10):
    '''
    SPE的KeyGen函数，生成主密钥msk。msk=(sk_0,d)

    Parameters:
    sec_parameter：security参数，默认为128位
    d：一个w支持的最大删除次数，默认为10

    Returns:
    msk_0：一个元组，储存初始的主密钥。sk_0为128位的bytes，d是一个整数
    '''

    # 随机生成sk_0
    sk_0 = hmac.new(b'sk_0').digest()

    msk = [sk_0, d]

    return msk






def Enc(msk_0, msg, t):
    '''
    SPE的Enc函数，计算得到m的密文ct

    Parameters:
    msk_0：一个元组，储存初始的主密钥。sk_0为128位的bytes，d是一个整数
    msg：要加密的msg，默认为256位（32字节）
    t：msg的tag，默认为128位

    Returns:
    ct：密文，默认为256位
    '''
    # 从msk_0处获取sk_0和d
    sk_0 = msk_0[0]
    d = msk_0[1]

    # 储存所有得到的sk
    sk = [sk_0]

    # 迭代计算sk_i,i属于[1,d]。储存在sk列表中
    # sk_i=H(sk_i-1,i)
    for i in range(1, d+1):
        sk_i = hmac.new(sk[-1]+int(i).to_bytes(16, 'big', signed=True)).digest()
        sk.append(sk_i)

    # 计算k=xor F(sk_i,t)
    # f储存所有的F计算值
    f = []
    for i in range(d+1):
        # 计算F(sk_i,t)
        f.append(PPRF_cal(sk[i], t))

    k = batch_xor(f)

    # 用AES和k加密msg
    # ct = AES.new(key=int(5).to_bytes(16,'big',signed=True), mode=AES.MODE_ECB).encrypt(msg)
    ct = AES.new(key=k, mode=AES.MODE_ECB).encrypt(msg)

    return ct


def Pun(msk_old, t, order):
    '''
    SPE的Pun函数，对tag t进行穿刺得到新的SK_new、由于是INC_Puc，所以只需要msk_old

    Parameters:
    msk_old：旧的msk，一个list容器，包含[sk_old,d]
    t：要被穿刺的tag
    order：该w被穿刺的次数，从1开始

    Returns:
    msk_new:新的msk，一个list容器，包含[sk_new,d]
    psk：新产生的穿刺密钥，一个list容器。其中包含2个元素。第一个元素储存sk，第二个list储存所有可达的前缀路径 
    '''
    # 从msk_old处获取sk_old和d
    sk_old = msk_old[0]
    d = msk_old[1]

    # 计算psk
    psk=PPRF_punc(t,sk_old)
    
    # 计算新的sk=H(sk_old,i)
    sk_new=hmac.new(sk_old+int(order).to_bytes(16,'big',signed=True)).digest()    

    # 计算msk_new
    msk_new=[sk_new,d]
    
    return msk_new,psk


def Dec(SK, ct, t):
    '''
    SPE的Dec函数，使用SK对密文st进行解密得到msg

    Parameters:
    SK：一个list容器，包含[msk,psk1,psk2,...,psk_i]
    ct：密文
    t：密文的tag。默认为128位的bytes

    Returns:
    msg：解密结果。返回bytes或者none（表示这个t被穿刺过）
    '''
    # 从msk获得sk_i和d
    msk=SK[0]
    sk_i=msk[0]
    d=msk[1]       


    # 判断i和d的关系，i就是w上进行穿刺操作的次数
    i=len(SK)-1
    
    # 储存sk值
    sk={i:sk_i}

    # 删除的数量没有达到上限，需要额外计算xor F(sk_i,t),i=i...d
    if i<d:
        # 计算sk_i,i=i..d        
        for j in range(i+1,d+1):
            sk[j]=hmac.new(sk[j-1]+int(j).to_bytes(16,'big',signed=True)).digest()
        
    
    # 计算k
    # 储存PPRF的值
    batch=[]    

    # 先计算xor F.eval(psk,t)
    for j in range(1,i+1):
        # 得到穿刺密钥psk
        psk=SK[j]

        # 使用穿刺密钥计算值。若结果为none，直接返回
        v=PPRF_eval(psk,t)
        if v is None:
            return
        batch.append(v)

    
    # 对sk中的元素计算F(sk,t)
    for j in sk:
        sk_j=sk[j]
        # 计算F.cal(sk,t)
        batch.append(PPRF_cal(sk_j,t))
    

    # 对batch中的F值进行异或得到k
    k=batch_xor(batch)

    # 使用k对ct进行解密
    # msg=AES.new(key=int(5).to_bytes(16,'big',signed=True),mode=AES.MODE_ECB).decrypt(ct)  
    msg=AES.new(key=k,mode=AES.MODE_ECB).decrypt(ct)  
    
    return msg


def batch_xor(l):
    '''
    将list l中的所有数据逐个异或，返回异或值

    Parameters:
    l:一个list

    Returns:
    xor:异或值
    '''
    xor = int(0).to_bytes(16, 'big', signed=True)
    for i in l:
        xor = bytes(a ^ b for a, b in zip(xor, i))

    return xor


if __name__ == "__main__":
    # 输入256位的msg，128位的tag，进行加密、穿刺、解密
    msg1='I am zhaohongguang'.zfill(32).encode('utf-8')
    t1=hmac.new(msg1).digest()
    msg2='I am jingyanzhi'.zfill(32).encode('utf-8')
    t2=hmac.new(msg2).digest()
    msg3='I am wilra'.zfill(32).encode('utf-8')
    t3=hmac.new(msg3).digest()
    msg4='I am biginsulator'.zfill(32).encode('utf-8')
    t4=hmac.new(msg4).digest()

    # 设置d=4
    d=4

    # 生成密钥
    msk_0=KeyGen(128,4)
    print(msk_0)

    # 加密前两个msg
    ct1=Enc(msk_0,msg1,t1)
    ct2=Enc(msk_0,msg2,t2)

    # 解密前两个
    print(Dec([msk_0],ct1,t1))
    print(Dec([msk_0],ct2,t2))

    # 穿刺第二个msg
    msk_1,psk_1=Pun(msk_0,t2,1)

    # 重新解密前两个msg
    print(Dec([msk_1,psk_1],ct1,t1))
    print(Dec([msk_1,psk_1],ct2,t2))

    # 加密第3，4个
    ct3=Enc(msk_0,msg3,t3)
    ct4=Enc(msk_0,msg4,t4)

    # 解密
    print(Dec([msk_1,psk_1],ct3,t3))
    print(Dec([msk_1,psk_1],ct4,t4))

    # 穿刺第1个
    msk_2,psk_2=Pun(msk_1,t1,2)
    print(Dec([msk_2,psk_1,psk_2],ct1,t1))
    print(Dec([msk_2,psk_1,psk_2],ct2,t2))
    print(Dec([msk_2,psk_1,psk_2],ct3,t3))
    print(Dec([msk_2,psk_1,psk_2],ct4,t4))

    # 穿刺第4个
    msk_3,psk_3=Pun(msk_2,t4,3)
    print(Dec([msk_3,psk_1,psk_2,psk_3],ct1,t1))
    print(Dec([msk_3,psk_1,psk_2,psk_3],ct2,t2))
    print(Dec([msk_3,psk_1,psk_2,psk_3],ct3,t3))
    print(Dec([msk_3,psk_1,psk_2,psk_3],ct4,t4))

    # 穿刺第3个
    msk_4,psk_4=Pun(msk_3,t3,4)
    print(Dec([msk_4,psk_1,psk_2,psk_3,psk_4],ct1,t1))
    print(Dec([msk_4,psk_1,psk_2,psk_3,psk_4],ct2,t2))
    print(Dec([msk_4,psk_1,psk_2,psk_3,psk_4],ct3,t3))
    print(Dec([msk_4,psk_1,psk_2,psk_3,psk_4],ct4,t4))







    # a = int(1).to_bytes(16, 'big', signed=True)
    # b = int(2).to_bytes(16, 'big', signed=True)
    # l = [a, b]
    # print(batch_xor(l))

    # sk=int(8).to_bytes(2,'big',signed=True)
    # t=int(16).to_bytes(2,'big',signed=False)
    # psk=PPRF_punc(t,sk)
    # # t=int(18).to_bytes(2,'big',signed=False)
    # print(PPRF_eval(psk,t))

    # t=int(16).to_bytes(1,'big',signed=False)
    # sk=int(16).to_bytes(2,'big',signed=False)
    # print(PPRF_punc(t,sk))

    # data=int(256).to_bytes(2,'big',signed=True)
    # s=bin2str()
    # print(s)
