from datetime import datetime
from elasticsearch import Elasticsearch
from ims_database_base import ImsDatabaseBase
from elasticsearch import helpers
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('共耗时约 {:.2f} 秒'.format(time.time() - start))
        return res
    return wrapper


class ImsES(ImsDatabaseBase):

    def __init__(self, es, index='images', doc_type='data', timeout='10s', size=100, *args, **kwargs):
        self.es = es
        self.index = index
        self.doc_type = doc_type
        self.timeout = timeout
        self.size = size
        if es.indices.exists(index=index):
            self.es.indices.create(index=index, ignore=400)
        super(ImsES, self).__init__(*args, *kwargs)

    def search_single_record(self, rec, pre_filter=None):
        body = {
            "query": {
                "match": rec
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
        body = {
            "query": {
                "match_all": {}
            }
        }
        return self.es.search(index=self.index, doc_type=self.doc_type, body=body, size=1000)['hits']['hits']

    def insert_single_record(self, rec, refresh_after=False):
        rec['timestamp'] = datetime.now()
        return self.es.index(index=self.index, doc_type=self.doc_type,
                             body=rec, refresh=refresh_after)

    @ timer
    def insert_multiple_record(self, rec):
        action = [{
            "_index": self.index,
            "_type": self.doc_type,
            "_source": {
                "title": i
            }
        } for i in range(100)]
        helpers.bulk(self.es, action)

    def delete_siginle_record(self, rec):
        body = {
            "query": {
                "match": rec
            }
        }
        return self.es.delete_by_query(
            index=self.index, body=body, doc_type=self.doc_type, refresh=True)

    def delete_all_record(self):
        body = {
            "query": {
                "match_all": {}
            }
        }
        self.es.delete_by_query(
            index=self.index, body=body, doc_type=self.doc_type)
