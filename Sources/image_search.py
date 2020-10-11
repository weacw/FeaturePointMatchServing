import numpy as np
from annoy import AnnoyIndex
from cvmodule import CVModule
import pickle


class ImageSearch():
    def __init__(self, db_name):
        self.cvmodule = CVModule()
        try:
            self.f = 16000
            self.t = AnnoyIndex(self.f, 'angular')
            self.t.load(db_name)
        except BaseException as e:
            pass

    def find_vector(self, des):
        des = des.flatten()
        if des.size < 16000:
            des = np.concatenate([des, np.zeros(16000 - des.size)])
        data = self.t.get_nns_by_vector(des, n=5)
        return data

    def unload(self):
        self.t.unload()

    def get_item_vector_by_id(self, id):
        return np.array(self.t.get_item_vector(id)).reshape(500, 32).astype('uint8')

    def search_batch(self, targetVector):
        kn_results = self.find_vector(targetVector)
        result_table = dict()
        labels_table = []
        try:
            self.labels_db = open('cache/label_db.pickle', 'rb')
            labels_table = pickle.load(self.labels_db)
            self.labels_db.close()
        except BaseException as e:
            print(e)
            pass
        try:
            for data_index in kn_results:
                vector = self.get_item_vector_by_id(data_index)
                good = self.cvmodule.match(vector,targetVector) 
                if len(good) > 50:
                    result_table[labels_table[data_index]] = len(good)
        except BaseException as ex:
            print(ex)
            pass
        return dict(sorted(result_table.items(),
                           key=lambda x: x[1], reverse=True))
