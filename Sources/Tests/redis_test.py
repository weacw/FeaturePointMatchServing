import numpy as np
import redis
import sys
sys.path.append('../')
from ImageMatch.Cores import *
from ImageMatch.Cores.Utitliy import timer

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
with open('t.txt','w') as f:
    f.write(str(r.hgetall(0)))

# @timer
# def toRedis(arr: np.array) -> str:
#     arr_dtype = bytearray(str(arr.dtype), 'utf-8')
#     arr_shape = bytearray(','.join([str(a) for a in arr.shape]), 'utf-8')
#     sep = bytearray('|', 'utf-8')
#     arr_bytes = arr.ravel().tobytes()
#     to_return = arr_dtype + sep + arr_shape + sep + arr_bytes
#     return to_return
# @timer
# def fromRedis(serialized_arr: str) -> np.array:
#     sep = '|'.encode('utf-8')
#     i_0 = serialized_arr.find(sep)
#     i_1 = serialized_arr.find(sep, i_0 + 1)
#     arr_dtype = serialized_arr[:i_0].decode('utf-8')
#     arr_shape = tuple([int(a) for a in serialized_arr[i_0 + 1:i_1].decode('utf-8').split(',')])
#     arr_str = serialized_arr[i_1 + 1:]
#     arr = np.frombuffer(arr_str, dtype = arr_dtype).reshape(arr_shape)
#     return arr

# img = CVAlgorithm.path_to_image('../Tests/Benchmark/bq01.jpg')
# img = CVAlgorithm.crop_center(img, dim=(800,800))
# kps, des = CVAlgorithm.extract_feature(img)        

# record={
#     'id':0,
    
# }

# des1 = toRedis(des)
# des1 = fromRedis(des1)
# np.testing.assert_array_equal(des,des1)