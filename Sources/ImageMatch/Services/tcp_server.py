import zmq
import json
import base64
import threading
from random import choice



class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def start_server(self):
        context = zmq.Context()
        frontend = context.socket(zmq.REP)
        frontend.bind('tcp://*:4531')

        backend = context.socket(zmq.XREQ)
        backend.bind('inproc://backend')

        workers = []
        for i in range(4):
            worker = ServerWorker(context)
            worker.setName(f"MatchServer-{i}")
            # worker.setDaemon(True)
            worker.start()
            workers.append(worker)

        poll = zmq.Poller()
        poll.register(frontend, zmq.POLLIN)
        poll.register(backend,  zmq.POLLIN)

        while True:
            sockets = dict(poll.poll())

            # 客户端发来请求
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    msg = frontend.recv()                   
                    backend.send(msg)

            # TCP处理后端处理完毕反馈结果
            if backend in sockets:
                if sockets[backend] == zmq.POLLIN:
                    msg = backend.recv()                  
                    frontend.send(msg)

        frontend.close()
        backend.close()
        context.term()


class ServerWorker(threading.Thread):
    """ServerWorker"""

    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.XREQ)
        worker.connect('inproc://backend')
        print('Worker started')
        recvCount = 0
        while True:
            recv_data = worker.recv()
            if len(recv_data) > 5:
                data = self.predict()
                worker.send(json.dumps(data).encode('utf8'))
            else:
                worker.send(json.dumps({}).encode('utf8'))
            del recv_data

        worker.close()

    def predict(self):
        img = CVAlgorithm.read_base64(args['image_base64'])
        img = CVAlgorithm.crop_center(img, dim=(512,512))
        kps, des = CVAlgorithm.extract_feature(img)

        image_search = ImageSearch(annoy_index_db_path)
        result_table = image_search.search_batch(des, kps) 
        if result_table !=None:
            return result_table
        return {'message':'Can not found!'}

if __name__ == "__main__":
    server = Server()
    server.start_server()
    server.setDaemon(True)
    server.setName("ImageMatch")
    server.join()
