import cv2
import zmq
import json
import base64
import pickle
import threading
import numpy as np
from random import choice
from cvmodule import CVModule
from image_search import ImageSearch
from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch


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
        for i in range(2):
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
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    msg = frontend.recv()
                    # print('Server received %s' % (msg))
                    backend.send(msg)
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
        self.CVModule = CVModule()
        self.ims = ImsES(Elasticsearch())

    def run(self):
        worker = self.context.socket(zmq.XREQ)
        worker.connect('inproc://backend')
        print('Worker started')
        recvCount = 0
        while True:
            data = worker.recv()
            if len(data) > 5:
                img = self.CVModule.read_base64(data)
                crop_predict_img = self.CVModule.crop_center(img, int(
                    img.shape[0]*0.8), int(img.shape[0]*0.8))
                kp, des = self.CVModule.extract_feature(crop_predict_img)
                image_search = ImageSearch("cache/index.db")
                result_table = image_search.search_batch(des)
                   
                if len(result_table) > 0:
                    record = self.ims.search_single_record(
                        {'id': result_table['id']})
                    if len(record) > 0:
                        record.pop('des')
                        result_table = self.merge_dicts(record, result_table)
                        worker.send(json.dumps(result_table).encode('utf8'))
                else:
                    worker.send(json.dumps({}).encode('utf8'))
            del data

        worker.close()

    def merge_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3


server = Server()
server.start_server()
server.setDaemon(True)
server.setName("ImageMatch")
server.join()
