from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from datetime import datetime


es = Elasticsearch()
ims = ImsES(es)

ims.delete_siginle_record({'id': 0})

# record = ims.search_single_record({'id': "1"})
# if record:
#     record.pop('des')
#     print(record)

# print(ims.delete_siginle_record({'title': 90}))

# print(ims.search_single_record({'title': 90}))
# print(ims.delete_all_record())
# print(len(ims.search_all_record()))


# ims.delete_all_record()
