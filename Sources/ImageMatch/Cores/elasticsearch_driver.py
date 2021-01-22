from ImageMatch.Cores.ims_database_base import ImsDatabaseBase
from datetime import datetime

class ImsES(ImsDatabaseBase):
    def __init__(self, es, index='images', doc_type='data', timeout='10s', size=100, *args, **kwargs):
        self.es = es
        self.index = index
        self.doc_type = doc_type
        self.timeout = timeout
        self.size = size

        if not es.indices.exists(index=index):
            self.es.indices.create(index=index, ignore=400)
        super(ImsES, self).__init__(*args, *kwargs)

    
    def search_single_record(self, id):
        """查询单条数据

        Args:
            rec (dict): 需要匹配的条件          

        Returns:
            dict: 匹配到的数据
        """
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "id": id
                        }
                    }
                }
            }
        }

        res = self.es.search(index=self.index,
                             doc_type=self.doc_type,
                             body=body,
                             size=self.size,
                             timeout=self.timeout)['hits']['hits']

        # Avoid Empty error
        if len(res) > 0:
            res = res[0]['_source']
        else:
            res = {}
        return res

    def search_all_record(self):
        """检索所有数据

        Returns:
            es data: 所有数据
        """

        body = {
            "query": {
                "match_all": {}
            }
        }

        return self.es.search(index=self.index, doc_type=self.doc_type, body=body, size=1000)['hits']['hits']

    def insert_single_record(self, rec, refresh_after=False):
        """插入单行数据

        Args:
            rec ([dict]): [需要插入的数据]
            refresh_after (bool, optional): [插入后即可生效]]. Defaults to False.

        Returns:
            [es message]: [插入后返回消息]
        """

        rec['timestamp'] = datetime.now()
        return self.es.index(index=self.index,
                             doc_type=self.doc_type,
                             id=rec['id'],
                             body=rec,
                             refresh=refresh_after)


    def search_multiple_record(self, ids):
        """通过id数组进行一次性多个数据查询

        Args:
            ids (Array): 需要查询的Id数组

        Returns:
            dict: 查询到的所有数据
        """

        body = {
            "query": {
                "constant_score": {
                    "filter": {
                        "terms": {
                            "id": ids
                        }
                    }
                }
            }
        }
        res = self.es.search(index=self.index,
                             doc_type=self.doc_type,
                             body=body,
                             size=self.size,
                             timeout=self.timeout)['hits']['hits']
        return res

    def search_multiple_record_test(self, ids):
        """通过id数组进行一次性多个数据查询

        Args:
            ids (Array): 需要查询的Id数组

        Returns:
            dict: 查询到的所有数据
        """

        body = {
            '_source': ['id', 'metadata'],
            "query": {
                "terms": {
                    "id": ids
                }
            }
        }
        res = self.es.search(index=self.index,
                             doc_type=self.doc_type,
                             body=body,
                             size=self.size,
                             timeout=self.timeout)['hits']['hits']
        return res

    def insert_multiple_record(self, rec):
        """插入多行数据

        Args:
            rec (dict): 需要插入的数据
        """

        action = [{
            "_index": self.index,
            "_type": self.doc_type,
            "_source": {
                "title": i
            }
        } for i in range(100)]
        helpers.bulk(self.es, action)

    def delete_siginle_record(self, rec):
        """删除单条数据

        Args:
            rec (dict): 需要删除数据的匹配条件

        Returns:
            es message: 删除后es反馈回的消息
        """

        body = {
            "query": {
                "match": rec
            }
        }
        return self.es.delete_by_query(
            index=self.index, body=body, doc_type=self.doc_type, refresh=True)

    def delete_all_record(self):
        """移除所有ES数据集
        """

        body = {
            "query": {
                "match_all": {}
            }
        }
        self.es.delete_by_query(
            index=self.index, body=body, doc_type=self.doc_type)
