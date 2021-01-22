from ImageMatch.Cores import *
MIN_MATCH_COUNT = 10
shape = (100, 128)


class ImageSearch():
    def __init__(self, db_name):
        """初始化

        Args:
            db_name (string): 需要加载的数据库名称
        """
        self.annoyindx = AnnoyIndex_driver('cache/index.db')

    def find_vector(self, des):
        """通过向量匹配对应向量

        Args:
            des (vector): 需匹配向量

        Returns:
            vector: 匹配到的向量
        """
        return self.annoyindx.find_vector(des)

    def unload(self):
        self.annoyindx.unload()

    def get_item_vector_by_id(self, id):
        """通过数据库id获取该id对应的向量数据

        Args:
            id (int): 数据库id

        Returns:
            vector: 图像描述符向量
        """
        return self.annoyindx.get_item_vector_by_id(id, shape)

    def get_count(self):
        """获取当前annoy index数据库的个数

        Returns:
            int: 当前存在数据库内的数据个数
        """
        return self.annoyindx.get_count()

    def search_batch(self, targetVector,kps):
        """批量检索相似向量

        Args:
            targetVector (向量): 图像描述符的向量

        Returns:
            Dict: 检索到最为匹配的图像数据
        """
        self.annoyindx.loadDb()
        kn_results = self.find_vector(targetVector)        
        
        for data_index in kn_results:
            data_caches_es = ims.search_single_record(data_index)
            flatten_vector = data_caches_es['des']

            # 避免无法重塑形状
            if len(flatten_vector) > 12800:
                vector = self.annoyindx.reshape(
                    flatten_vector, (int(len(flatten_vector)/128), 128))
            else:
                vector = self.annoyindx.reshape(flatten_vector, (100, 128))

            good = CVAlgorithm.match(targetVector, vector)

            if len(good) > MIN_MATCH_COUNT:
                RANSAC_percent = CVAlgorithm.findHomgraphy(good, kps, data_caches_es['kps'])
                if RANSAC_percent >= 0.5:
                    data_caches_es['matchscore'] = len(good)       
                    data_caches_es.pop('des')
                    data_caches_es.pop('kps')             
                    return data_caches_es      
        return None

    def result_sort(self, e):
        return e['matchscore']
