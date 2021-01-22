from annoy import AnnoyIndex
import numpy as np
import os


class AnnoyIndex_driver():
    def __init__(self, _db_path, _metric='manhattan',  _reshape=(100, 128)):
        self.vector_size = 1024
        self.db_path = _db_path
        self.metric = _metric
        self.shape = _reshape
        self.annoyindex = AnnoyIndex(self.vector_size, self.metric)

    def loadDb(self):
        if os.path.exists(self.db_path):
            self.annoyindex.load(self.db_path)

    def find_vector(self, des):
        """通过向量匹配对应向量

        Args:
            des (vector): 需匹配向量

        Returns:
            vector: 匹配到的向量
        """
        if des is None:
            return
        des = des.ravel()[: self.vector_size]
        if des.size < self.vector_size:
            des = np.concatenate([des, np.zeros(self.vector_size - des.size)])
        data_tuple = self.annoyindex.get_nns_by_vector(des, n=15, include_distances=True)        
        
        #过滤，相似距离大于32000的图像
        data = list()
        for data_inex in range(0, len(data_tuple[0])):
            if data_tuple[1][data_inex] > 32000:
                break
            data.append(data_tuple[0][data_inex])
        return data

    def unload(self):
        self.annoyindex.unload()

    def get_item_vector_by_id(self, id):
        """通过数据库id获取该id对应的向量数据

        Args:
            id (int): 数据库id

        Returns:
            vector: 图像描述符向量
        """
        return np.array(self.annoyindex.get_item_vector(id)).reshape(self.shape).astype('float32')
    def reshape(self, des, shape):
        siez = shape[0]*shape[1]
        if len(des) < siez:
            des = np.concatenate([des, np.zeros(siez - len(des))])
        return np.array(des).reshape(shape).astype('float32')

    def get_count(self):
        """获取当前annoy index数据库的个数

        Returns:
            int: 当前存在数据库内的数据个数
        """
        return self.annoyindex.get_n_items()

    def buildAnnoyIndexDB(self, vectorGroup):
        """用于生成追踪数据库

        Args:
            db_name (string): 数据库名称
            vectorGroup (vector):向量组
        Returns:
            Bool: True即为构建数据库成功，反之则为失败
        """

        try:
            self.annoyindex.unload()
            for e in vectorGroup:
                des = e['des'][:self.vector_size]
                id = e['id']
                if des.size < self.vector_size:
                    des = np.concatenate(
                        [des, np.zeros(self.vector_size - des.size)])
                self.annoyindex.add_item(id, des)
            self.annoyindex.build(100)
            self.annoyindex.save(self.db_path)            
            return True
        except Exception as e:
            print(e)
            return False
