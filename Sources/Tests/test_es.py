import sys
from datetime import datetime
import os
sys.path.append("..") 
from ImageMatch.Cores import *
from ImageMatch.Cores.Utitliy import timer

es = Elasticsearch()
ims = ImsES(es)

cache_path ='../cache/index.db'
# image_search = ImageSearch(cache_path)
# image_count = image_search.get_count()
# image_search.unload()
# print(image_count)

ims.delete_all_record()
print(len(ims.search_all_record()))
if os.path.exists(cache_path):
    os.remove(cache_path)

# ims.insert_single_record({"id":1100,"metadata":100},True)
# record = ims.search_single_record({'id': "1100"})
# print(record)

# ims.delete_siginle_record({'id': 1})
@timer
def test():    
    record = ims.search_single_record(0)
    if record:
        record.pop('des')
        record.pop('kps')
        print(record)
test()
# results = ims.search_multiple_record([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
# print(len(results))
# for result in results:
#     source = result['_source']
#     source.pop('des')
#     source.pop('kps')
#     print(source)

# print(ims.delete_siginle_record({'title': 90}))

# print(ims.search_single_record({'title': 90}))
# print(ims.delete_all_record())
print(len(ims.search_all_record()))


# ims.delete_all_record()
# all_records = ims.search_all_record()
# count = 0
# for e in all_records:
#     file = open(f'../description/{count}.txt','w')
#     file.write(str(e))
#     count+=1