import numpy as np
from annoy import AnnoyIndex
from cvmodule import CVModule



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
        if des is None:
            return
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
        try:            
            for data_index in kn_results:
                vector = self.get_item_vector_by_id(data_index)
                good = self.cvmodule.match(vector, targetVector)                
                if len(good) > 50:
                    result_table['id'] = data_index
                    result_table['matchscore'] = len(good)
                    break
        except BaseException as ex:
            print(ex)
            pass
        return dict(sorted(result_table.items(),
                           key=lambda x: x[0][1], reverse=False))

    def get_count(self):
        return self.t.get_n_items()
