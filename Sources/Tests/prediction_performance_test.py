#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import base64
import time
import sys
def ms(): return int(round(time.time()*1000))


class TcpSocketClient():
    def __init__(self):
        with open("Benchmark/bq04.jpg", "rb") as f:
            self.base64_data = base64.b64encode(f.read())
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)

    def start(self):
        self.socket.connect("tcp://localhost:4531")

    def sendmsg(self):
        self.socket.send(self.base64_data)

    def recv(self):
        return self.socket.recv()


class Record():
    def __init__(self, lastTime, count):
        self.lastTime = lastTime
        self.count = count

    def Communicate(self, tcp, i):
        tcp.sendmsg()
        if (ms()-self.lastTime)/1000 > 1:
            print("Rate = {}".format(i-self.count))
            self.count = i
            self.lastTime = ms()
        print(tcp.recv())
        


if __name__ == "__main__":
    tcp = TcpSocketClient()
    tcp.start()
    # tcp.sendmsg()
    # print(tcp.recv())
    record = Record(ms(), 0)
    for i in range(1, 150):
        # tcp.sendmsg()
        record.Communicate(tcp,i)
        # if (ms() - record.lastTime)/1000 > 1:
        #     print("Rate = {}".format(i-record.count))
        #     record.count = i
        #     record.lastTime = ms()
