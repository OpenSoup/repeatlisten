以事件的方式管理tcp的链接与接收。  
如果您的设备已安装pip,您可以打开命令行，并使用以下代码进行安装：
```
pip install --trusted-host 114.115.172.126 -i http://114.115.172.126:3141/simple/ repeatlisten
```
以下是一些演示代码：
```python
from repeatListen import *


class ServerEvent:
    def __init__(self, conn, addr):
        """
        在有新的连接时调用该函数
        :param conn: 连接对应的方法类<socket>
        :param addr: ip地址和端口号(ip地址<str>, 端口号<int>)
        """
        self.conn, self.addr = conn, addr  # 添加类成员变量，记录链接对应的方法类和地址
        print(f"{addr}: connected.")       # 输出链接信息

    def recv(self, data):
        """
        在接收到数据时调用的函数
        :param data: 接收到的数据
        :return: None
        """
        print(f"{self.addr}: send a message: {data}")  # 输出ip地址与接收到的消息

    def timeout(self):
        """
        在连接因响应超时而断开时调用的函数，调用该函数时不会调用close函数
        :return: None
        """
        print(f"{self.addr}: connect closed: timeout")  # 输出超时消息

    def close(self):
        """
        在断开连接时调用的函数
        :return: None
        """
        print(f"{self.addr}: connect closed")  # 输出链接关闭的消息


if __name__ == '__main__':
    server = RepeatListen(port=11451, funk_class=ServerEvent)
    server.start()
```
这段代码运行后，当有客户机链接您的设备的11451端口号时，会输出：
```
('客户机ip地址', 客户机端口号): connected.
```
当客户发送“hello from conn”的二进制数据时，会输出：
```
('客户机ip地址', 客户机端口号): send a message: b'hello from conn'
```
当链接断开时，会输出：
```
('客户机ip地址', 客户机端口号): connect closed
```
当数据返回超时时，会输出：
```
('客户机ip地址', 客户机端口号): connect closed: timeout
```
