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
from Utitliy import get_image_b64,timer
dim_800x800=(800,800)
annoy_index_db_path='cache/index.db'
class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def start_server(self):
        context = zmq.Context()
        frontend = context.socket(zmq.XREP)
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
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    msg = frontend.recv()
                    # print('Server received %s' % (msg))
                    backend.send(msg)
            if backend in sockets:
                if sockets[backend] == zmq.POLLIN:
                    msg = backend.recv()
                    print(msg)
                    frontend.send(msg)

        frontend.close()
        backend.close()
        context.term()


class ServerWorker(threading.Thread):
    """ServerWorker"""

    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        self.image_search = ImageSearch(annoy_index_db_path)

    def run(self):
        worker = self.context.socket(zmq.XREQ)
        worker.connect('inproc://backend')
        print('Worker started')
        recvCount = 0
        while True:
            recv_data = worker.recv()
            if len(recv_data) > 5:
                img = get_image_b64(self.CVAlgorithm,recv_data)
                img = self.CVAlgorithm.crop_center(img, dim=dim_800x800)
                kps, des = self.CVAlgorithm.extract_feature(img)
                result_table = self.image_search.search_batch(des)
                # Collection  the id fields
                result_ids_table = list()
                [result_ids_table.append(result['id']) for result in result_table]
                records = self.ims.search_multiple_record(result_ids_table)
                # Check the result length, when the result length is greater than 0, get the matching data
                for data_index in range(len(result_table)):
                    record = records[data_index]["_source"]
                    data = result_table[data_index]
                    RANSAC_percent = self.CVAlgorithm.findHomgraphy(
                        data['good'], kps, record['kps'])
                    if len(record) > 0 and RANSAC_percent > 0.5:
                        # Remove the field of des. Because the des field is storing the image description data
                        record.pop('des')
                        record.pop('kps')
                        data.pop('good')
                        data['confidence'] = RANSAC_percent
                        data = self.merge_dicts(data, record)
                        worker.send(json.dumps(data).encode('utf8'))
            else:
                worker.send(json.dumps({}).encode('utf8'))
            del recv_data

        worker.close()

    def merge_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3


if __name__ == "__main__":
    server = Server()
    server.start_server()
    # server.setDaemon(True)
    server.setName("ImageMatch")
    server.join()
