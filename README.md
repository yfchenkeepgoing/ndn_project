# introdcue
## start
####It is very simple to use, just execute ./shell.sh 0 to start a node. Any number of nodes can be started in this system
#### command:  ./shell.sh 0  ./shell.sh 1  ./shell.sh 2   ./shell.sh 3  ./shell.sh 4

## Query data
####You can use this interface to access data:http://127.0.0.1:33351/r0/humidity http://localhost:33351/r0/humidity  
we can change the node r0 to r1 ... r5

#### you also can change temperature to wind speed or humidity

可以修改的几处地方：
1、可以定义一个工具类，将几个常用的函数全部写进去，比如hashstr，get_host_ip，以避免重复写这些基本的函数，然后在每个python文件中引用工具类即可
2、hashstr函数可以采用更复杂的哈希算法，比如SHA-256，以提高安全性
3、可以将client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)写为client = socket.SocketType(family = socket.AF_INET, type = socket.SOCK_STREAM)，这样写更易于理解
4、sensor.py和web.py中都定义了class Client，可以单独写一个文件来定义class Client，然后在sensor.py和web.py中import这个类
5、可以写一个脚本实时获取天气信息并存入csv文件中，这样离真实的传感器就更接近了
6、web.py中本来创建的是flask应用，可以用别的框架或者socket创建一个其他应用，从而产生另外的展示界面

学习记录：
1、没有完全理解代码
2、可以在一台设备上开启一个节点，现在的问题是如何在多台设备上开启多个节点
3、web.py中的client函数的作用是什么？谁是client
我目前的理解是通过创建socket监听了本地的POD_PORT端口，并向该端口发送clientMessage，并返回本地的POD_PORT端口的返回值
在此过程中，本地扮演的角色是服务器（本地是NDN的一个节点，既可以扮演服务器也可以扮演客户端）
这相当于根据clientMessage中包含的信息在本地查找相应的结果，然后返回并显示在网页上
web.py中的POD_PORT是返回查询结果的端口，初始编号是33335，web_basic_port是网页上需要访问的端口，初始编号是33350
4、注意，要等到项目完全启动起来，即打印出point dict_keys(['r0'])的信息后（大概需要半分钟），才可以从网页上访问到相应的结果
5、为什么sensor.py和client.py中都定义了class Client，这样会导致混淆吗？
6、a.py是一个另外定义的本地服务器，应该是用于调试的，在启动这个项目的时候不需要这个文件也可以正常启动
7、如何理解这个项目中的众多接口和端口？
8、server.py中实现了当有server中有client请求的信息时，就发送该信息给client，如果没有client请求的信息时，就将该信息发送给与该节点相连的其他server
9、展示在网页上的数据是如何被从数据表格中抽取出来的？
10、本项目查找的是目标信息的哈希值，既不是查找目标信息本身，也不是查找其地址
11、兴趣包与数据包是一一对应的
12、server.py中会先读入来自传感器的数据，然后将该数据的哈希值存入字典中，再将该数据的类型改为interest，然后将其插入到interest_queue中，通过interest_queue函数将其转发给服务器的相邻节点，这就是兴趣包的产生
兴趣包可以说除了键值和数据包不同，哈希值也和数据包不同，其内容是和一一对应的数据包完全相同的
一组数据包和兴趣包中应该只有键值不同，一者的类型是data，另一者的类型是interest，所以存储兴趣包的content name的值的哈希值，用于后续有匹配的数据包的content name的哈希值来查找，若两哈希值一样，则说明这一对interest包和data包是匹配的
一个兴趣包的结构：
{'type': 'interest', 'interest_ID': '20000', 'content_name': 'r6/91'}
一个与之对应的数据包的结构：
{'type': 'data', 'interest_ID': '20000', 'content_name': 'r6/91'}，我猜测还有一个data的键，其值是一个具体的数字
13、兴趣包和数据包的结构是怎样的？分别在哪里定义了？
兴趣包定义在interests.py中
14、如何在不同的设备上运行这个项目，如何在一个设备上查询传输到其他设备上的传感器数据，在哪里可以显示出这个数据
15、interests.py中的interest数组似乎就是由外部输入的，外部需要传入interest_ID和content name这两个参数
interest数组可能来自server.py中的interest_queue，尽管interest_queue没有给interest显示地传入参数
16、为什么要指定代码为python2.6，用python3不好吗？
17、interests.py中的Outface似乎也是一个需要我输入的参数
我应该是要输入interest数组，再输入传入interest数组的节点Outface
18、client.py中的内容也没有在项目的其他文件中被显示地调用，应该可以在另外一台服务器上单独运行client.py，传入相应的请求参数，然后收到返回结果
19、data.py中的Send_data(self, Infaces, fib, data)函数中的各项参数是从哪里传入的？疑似是从server.py中传入的

问题：
1、可以在一台设备上开启一个节点，现在的问题是如何在多台设备上开启多个节点
2、为什么sensor.py和client.py中都定义了class Client，这样会导致混淆吗？
3、a.py和test.py的作用是什么？似乎没有这两个文件项目也可以正常启动
4、如何理解这个项目中的众多接口和端口？
5、展示在网页上的数据是如何被从数据表格中抽取出来的？
6、数据包的结构是怎样的？在哪里定义了？
7、如何在不同的设备上运行这个项目，如何在一个设备上查询传输到其他设备上的传感器数据，在哪里可以显示出这个数据？
8、interests.py中的interest数组和Outface是在哪里输入的？
9、为什么要指定代码为python2.6，用python3不好吗？
10、client.py中的内容也没有在项目的其他文件中被显示地调用，其作用是什么？如何使用client.py？
11、data.py中的Send_data(self, Infaces, fib, data)函数中的各项参数是从哪里传入的？

学习记录_update：
1、呈现数据的网页是每隔一段时间刷新一次，大概是三分多钟，不会实时刷新，时间和information都会刷新
查看sensor.py函数可以看出，这个间隔具体来说是200秒，因为time.sleep(200)，每隔200秒节点从传感器读取一次数据
应该是没过一段时间模拟出来的传感器就会收到一次信息（本质是从数据表格中随机读取一些信息），然后server完成一些操作，就可以呈现在网页上
2、sensor类型的数据是节点从传感器处读取的数据包，interest类型的数据是sensor类型的数据直接改变类型（Type: sensor->interest）得到的，data类型的数据是节点之间流动的数据包
因此interests.py这个文件应该是多余的，因为所有interest类型的数据都是直接由sensor类型的数据生成的
3、若程序报错，可能是网页的端口被占用了，注意修改呈现网页的端口
4、多余的需要删去的文件：a.py(server.py的简化版，用于调试服务器方法), client.py(被sensor.py取代了), test.py(测试文件，现在里面啥也没写), interests.py（interest类型的数据包直接由sensor类型的数据包转化而来）
5、本程序最后实现了通过查询城市名称（r0/r1/r2）而不是访问数据所在的地址来查找数据，这与named data networking的概念想契合，网页上呈现的数据是从表格中随机读取的，但每过200秒会刷新一次
6、本程序采用的是去中心化p2p的网络拓扑结构，可以有效的防范单点故障
7、本项目似乎只能用到最多6台服务器上，用到7台服务器时就会出现报错，原因在于fib函数采用了一种简化的分为两层的方式，没有采用真正的fib函数的正规写法
8、如何将本程序扩展到百万台设备上？
可以将百万台设备每一万台编成一组，共100组，这每一组中选出10台服务器作为中心节点，然后让这1000台服务器之间相互通信交换数据
选择10台服务器的原因是防止单点故障，提高系统的可靠性（高可用性），这种策略可以通过各种方式实现，例如使用负载均衡器来分配流量，或设置主动-被动（active-passive）或主动-主动（active-active）的冗余配置。
主动-被动配置：其中一台服务器（主动服务器）处理所有请求，而另一台服务器（被动服务器）在主动服务器出现故障时接管工作。
主动-主动配置：两台服务器都在处理请求，如果一台出现故障，另一台接管其全部或部分工作负载。
这种做法有助于确保系统的连续运行和服务的稳定性，特别是在对业务连续性有较高要求的环境中。
9、我删去了4中所说的多余文件，还需要在server.py中将调用了interests.py中的class INTEREST的部分给删掉，删完后，代码可以在本机上正常运行

todo:
1、修改sensor.py中的fib函数，将其改为table互相查找的形式，或者换一种最短路算法，比如dijkstra
2、重构代码，可以定义一个工具类，将几个常用的函数全部写进去，比如hashstr，get_host_ip，以避免重复写这些基本的函数，然后在每个python文件中引用工具类即可
3、将城市由r0/r1/r2改为实际的城市，比如dublin, cork, beijing等等
4、修复页面显示中的单位，目前的单位似乎是乱码
5、调用一个实时获取天气数据的api，取代利用sensor.py从表格中读取数据的方式
6、可以适当缩短数据更新的时间间隔，减小sensor.py中的time.sleep，让程序更接近实时的获取数据
7、给本项目寻找一个新的应用场景







