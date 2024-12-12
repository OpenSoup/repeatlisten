"""
提供tcp协议的多线程服务
"""
import socket
from time import*
from threading import *
from socket import *


class RepeatListenDFC:  # RepeatListen default function class
    """
    RepeatListen默认调用此方法类,可直接复制此类作为参考
    """
    def __init__(self, conn, addr):
        """
        在有新的连接时调用该函数
        :param conn: 连接对应的方法类<socket>
        :param addr: ip地址和端口号(ip地址<str>, 端口号<int>)
        """
        ...

    def recv(self, data):
        """
        在接收到数据时调用的函数
        :param data: 接收到的数据
        :return: None
        """
        ...

    def timeout(self):
        """
        在连接因响应超时而断开时调用的函数，调用该函数时不会调用close函数
        :return: None
        """
        ...

    def close(self):
        """
        在断开连接时调用的函数
        :return: None
        """
        ...


class RepeatListen:
    def __init__(self, ip='0.0.0.0', port=None, time_out=60, funk_class=RepeatListenDFC, log_error=False):
        """
        重复监听，监听到一个连接后，在接收这个连接的数据的同时，监听下一个连接
        :param ip:         ip地址
        :param port:       端口号
        :param time_out:   判断响应超时的时间，在距离上次接收到数据或连接的时间超过time_out秒后断开连接
        :param funk_class: 方法类，在监听到连接时创建一个该类，并在该连接有动作时执行该类中对应的方法，执行的具体方式如下
                           当监听到连接时，执行：
                               funk_class(连接对应的方法类<socket>, (ip地址<str>, 端口号<int>))
                           当接收到数据时，执行：
                               funk_class.recv(连接对应的方法类<socket>, (ip地址<str>, 端口号<int>), 接收到的数据)
                           当响应超时时，执行：
                               funk_class.timeout(连接对应的方法类<socket>, (ip地址<str>, 端口号<int>))
                           当断开连接时，执行:
                               funk_class.close(连接对应的方法类<socket>, (ip地址<str>, 端口号<int>))
        """
        if port is None:
            raise Exception('missing a parm: port')
        self.stop = False
        self.time_out = time_out
        self.funk_class = funk_class
        self.log_error = log_error
        self.conn_dict = {}

        self.server = socket(AF_INET, SOCK_STREAM)  # 创建服务端
        self.server.setblocking(False)
        self.server.bind((ip, port))  # 开放服务器端口

    def __del__(self):
        """
        当该对象被删除后，停止该对象进行的一切行为
        :return: None
        """
        self.stop = True
        [self.conn_dict[addr].close() for addr in self.conn_dict]

    def __repeat_recv(self, conn: socket, addr, funk_class: RepeatListenDFC):
        """
        ！！！内部函数，请勿在外部调用！！！
        重复接收数据，
        当有数据时，执行用户提供的对应函数
        当断开连接时，执行用户提供的对应函数
        当接收超时时，执行用户提供的对应函数

        :param conn: 连接对应的方法类<socket>
        :param addr: ip地址和端口号(ip地址<str>, 端口号<int>)
        :return: None
        """
        recv_time = time()

        my_key = f"{addr[0]}:{addr[1]}"
        self.conn_dict[my_key] = conn
        while True:  # 主循环
            try:  # 尝试接收数据
                message = conn.recv(2048)
                recv_time = time()
                if message == b'':  # 当接收到空数据，即对方主动断开连接，调用用户提供的对应函数，并退出循环
                    funk_class.close()  # 调用用户提供的对应函数
                    break
                funk_class.recv(message)  # 调用用户提供的对应函数
            except BlockingIOError:
                ...
            except BaseException as BE:
                if self.log_error:
                    print(repr(BE))
            if time() >= recv_time+self.time_out:
                funk_class.timeout()  # 调用用户提供的对应函数
                break
            if self.stop:
                break
            sleep(0)
        conn.close()
        del self.conn_dict[my_key]

    def broadcast(self, data):
        """
        广播消息，让所有连接到服务器的用户接收到这条消息
        :param data: 广播的消息
        :return: None
        """
        [self.conn_dict[addr].send(data) for addr in self.conn_dict]

    def getAllConn(self):
        return self.conn_dict

    def start(self):
        """
        开始服务，即循环监听开始，当监听到连接时，多线程执行self.__repeat_recv(conn, addr)并执行用户提供的对应函数
        :return: None
        """
        while True:
            try:
                self.server.listen()
                conn, addr = self.server.accept()
                funk_class = self.funk_class(conn, addr)  # 调用用户提供的对应类
                conn.setblocking(False)
                run_t = Thread(target=self.__repeat_recv, args=(conn, addr, funk_class))
                run_t.start()
            except BlockingIOError:
                ...
            if self.stop:
                break
            sleep(0)

    def destroy(self):
        """
        摧毁该方法类
        :return: None
        """
        self.stop = True
        del self


if __name__ == '__main__':
    server = RepeatListen()
