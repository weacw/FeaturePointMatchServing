import sys
from datetime import datetime
sys.path.append("..") 
from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch


es = Elasticsearch()
ims = ImsES(es)
# ims.delete_all_record()
# print(len(ims.search_all_record()))
# ims.delete_siginle_record({'id': 1})

# record = ims.search_single_record({'id': "1"})
# if record:
#     record.pop('des')
#     print(record)

# print(ims.delete_siginle_record({'title': 90}))

# print(ims.search_single_record({'title': 90}))
# print(ims.delete_all_record())
# print(len(ims.search_all_record()))


ims.delete_all_record()
# all_records = ims.search_all_record()
# count = 0
# for e in all_records:
#     file = open(f'../description/{count}.txt','w')
#     file.write(str(e))
#     count+=1