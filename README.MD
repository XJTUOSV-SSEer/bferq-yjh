### File Structure

~~~
│  README.MD
└─src
    ├─BFERQ								//储存AR-DSSE方案的源码
    │  │  abi.json							//智能合约对应的abi
    │  │  blockchain.py						//client、server与区块链通信相关的源码
    │  │  Bytecode							//智能合约的字节码
    │  │  client.py							//client端源码
    │  │  contract.sol						//智能合约源码					
    │  │  experiment.py						//不同数据集测试性能源码
    │  │  main.py							//测试代码
    │  │  server.py							//server端源码
    │  │  tansform_data.py					//生成不同大小的数据集
    │  │  v0_case1_dump.txt					//测试代码中第1个测试点的标准结果
    │  │  v0_case2_dump.txt					//测试代码中第2个测试点的标准结果
    │  │  
    │  ├─.vscode
    │  │      settings.json				
    │  └─__pycache__
    │          client.cpython-36.pyc
    │          server.cpython-36.pyc
    │          
    ├─BFERQBF							//储存AR-DSSE方案的源码
    │  │  abi.json							//智能合约对应的abi
    │  │  blockchain.py						//client、server与区块链通信相关的源码
    │  │  client.py							//client端源码
    │  │  contract.sol						//智能合约源码	
    │  │  experiment.py						//不同数据集测试性能源码
    │  │  main.py							//测试代码
    │  │  server.py							//server端源码
    │  │  SPE.py							//测试性能时使用的可刺穿的对称加密(SPE)源码
    │  │  SPE_old.py						//根据Sun等论文实现的可刺穿的SPE源码
    │  │  tansform_data.py					//生成不同大小的数据集
    │  │  v1_case1_dump.txt					//测试代码中第1个测试点的标准结果
    │  │  v1_case2_dump.txt					//测试代码中第2个测试点的标准结果
    │  │  v1_case6_dump.txt					//测试代码中第6个测试点的标准结果
    │  │  v1_case7_dump.txt					//测试代码中第7个测试点的标准结果
    │  │  
    │  └─.vscode
    │          settings.json
    │         
    ├─data									//测试性能所需的数据
    │      data_10K.json
    │      data_10K.txt
    │      data_1200.json
    │      data_1200.txt
    │      data_1600.json
    │      data_1600.txt
    │      data_2000.json
    │      data_2000.txt
    │      data_2K.json
    │      data_2K.txt
    │      data_400.json
    │      data_400.txt
    │      data_4K.json
    │      data_4K.txt
    │      data_6K.json
    │      data_6K.txt
    │      data_800.json
    │      data_800.txt
    │      data_8K.json
    │      data_8K.txt
    │      data_del_1K.json
    │      data_del_1K.txt
    │      data_del_2K.json
    │      data_del_2K.txt
    │      data_del_3K.json
    │      data_del_3K.txt
    │      data_del_4K.json
    │      data_del_4K.txt
    │      data_del_5K.json
    │      data_del_5K.txt
~~~







### Prepare Environment

操作系统: Ubuntu 18.04

python 3.6.9

Docker 中安装 testRPC





### Building Procedure

首先启动Docker和testRPC

~~~
sudo docker run --detach --publish 8545:8545 trufflesuite/ganache-cli:latest
remixd -s /Users/yujiahe123/remixPath https://remix.ethereum.org/

ACCOUNT ADDRESS
0x6bA9388c3FB86Bb5215F6168f5f7E79B5270C6D8
PRIVATE KEY
0x7985e0974cc77a87300e51a02c187c0977d92ed04a346a6fce9873c05966b0d5


~~~

然后在Remix中连接测试网络，并将智能合约部署至测试网络。