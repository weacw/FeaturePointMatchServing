from ImageMatch.Cores.ims_database_base import ImsDatabaseBase
from datetime import datetime
import redis
from ImageMatch.Cores.Utitliy import *


class redis_driver():
    def search_single_record(self, rec, pre_filter=None):
        return self.r.hgetall(rec['id'])

    def insert_single_record(self, rec):
        self.r.hmset(rec['id'], rec)

    def insert_multiple_record(self, rec):
        self.r.hmset(rec['id'], rec)

    def delete_single_record(self, rec):
        raise NotImplementedError

    def search_all_record(self):
        all_record = []
        all_keys = self.r.keys()
        for key in all_keys:
            # self.r.delete(key)
            all_record.append(self.r.hgetall(key))
        return all_record

    def __init__(self, *args, **kwargs):
        self.pool = redis.ConnectionPool(
            host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(connection_pool=self.pool)

    @timer
    def search_multiple_record(self, ids):
        all_record = list()
        for id in ids:
            record = self.r.hgetall(id)
            all_record.append(record)
        return all_record
