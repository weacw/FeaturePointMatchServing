import numpy as np
# from annoy import AnnoyIndex
from cvmodule import CVModule
from annoyindex_driver import AnnoyIndex_driver
from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch


class ImageSearch():
    def __init__(self, db_name):
        """初始化

        Args:
            db_name (string): 需要加载的数据库名称
        """
        self.MIN_MATCH_COUNT = 10
        self.shape = (100, 128)
        self.cvmodule = CVModule()
        self.annoyindx = AnnoyIndex_driver(db_name)
        self.ims = ImsES(Elasticsearch())
        try:
            self.annoyindx.loadDb()
        except BaseException as e:
            pass

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
        return self.annoyindx.get_item_vector_by_id(id,self.shape)

    def get_count(self):
        """获取当前annoy index数据库的个数

        Returns:
            int: 当前存在数据库内的数据个数
        """
        return self.annoyindx.get_count()


    def search_batch(self, targetVector):
        """批量检索相似向量

        Args:
            targetVector (向量): 图像描述符的向量

        Returns:
            Dict: 检索到最为匹配的图像数据
        """
        kn_results = self.find_vector(targetVector)        
        result_table = list()
        good = None
        
        # terms检索 避免一次次检索浪费时间
        data_caches_es = self.ims.search_multiple_record(kn_results)

        try:
            for data_index in kn_results:
                record = dict()
                flatten_vector = data_caches_es[data_index]['_source']['des']

                # 避免无法重塑形状
                if len(flatten_vector) > 12800:
                    vector = self.annoyindx.reshape(flatten_vector,(101,128))
                else:
                    vector = self.annoyindx.reshape(flatten_vector,(100,128))

                # vector = self.get_item_vector_by_id(data_index)                
                good = self.cvmodule.match(targetVector, vector)

                if len(good) > self.MIN_MATCH_COUNT:
                    record['id'] = data_index
                    record['matchscore'] = len(good)
                    record['good'] = good
                    result_table.append(record)                    

        except BaseException as ex:
            print(ex)
            pass
        result_table.sort(key=self.result_sort, reverse=True)
        return result_table

    def result_sort(self, e):
        return e['matchscore']
