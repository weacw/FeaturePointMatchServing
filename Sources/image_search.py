import numpy as np
from annoy import AnnoyIndex
from cvmodule import CVModule


class ImageSearch():
    def __init__(self, db_name):
        """初始化

        Args:
            db_name (string): 需要加载的数据库名称
        """
        self.cvmodule = CVModule()
        try:
            self.f = 16000
            self.t = AnnoyIndex(self.f, 'angular')
            self.t.load(db_name)
        except BaseException as e:
            pass

    def find_vector(self, des):
        """通过向量匹配对应向量

        Args:
            des (vector): 需匹配向量

        Returns:
            vector: 匹配到的向量
        """
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
        """通过数据库id获取该id对应的向量数据

        Args:
            id (int): 数据库id

        Returns:
            vector: 图像描述符向量
        """
        return np.array(self.t.get_item_vector(id)).reshape(500, 32).astype('uint8')

    def search_batch(self, targetVector):
        """批量检索相似向量

        Args:
            targetVector (向量): 图像描述符的向量

        Returns:
            Dict: 检索到最为匹配的图像数据
        """
        kn_results = self.find_vector(targetVector)               
        result_table = dict()
        try:
            for data_index in kn_results:
                vector = self.get_item_vector_by_id(data_index)
                good = self.cvmodule.match(vector,targetVector)
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
        """获取当前annoy index数据库的个数

        Returns:
            int: 当前存在数据库内的数据个数
        """
        return self.t.get_n_items()
