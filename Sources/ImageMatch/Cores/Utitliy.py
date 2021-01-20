from flask_restful import reqparse
import werkzeug
import time
import numpy as np
import base64
import json
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('{:}Total time: {:.15f} s'.format(func, time.time() - start))
        return res
    return wrapper


def get_image(CVAlgorithm):
    parse = reqparse.RequestParser()
    parse.add_argument('image_url')
    parse.add_argument('image_base64')
    parse.add_argument(
        'image', type=werkzeug.datastructures.FileStorage, location='files')
    parse.add_argument('metadata')
    args = parse.parse_args()
    if args['image_url'] is not None:
        img = CVAlgorithm.url_to_image(args['image_url'])
    elif args['image'] is not None:
        img = CVAlgorithm.bytes_to_image(args['image'])
    return img, args


def get_image_b64(CVAlgorithm, _b64_data):
    return CVAlgorithm.read_base64(_b64_data)



def encode_vector(ar):
    return base64.encodestring(ar.tobytes()).decode('ascii')

def decode_vector(ar):
    return np.fromstring(base64.decodebytes(bytes(ar, 'ascii')), dtype='float32')

def encode_dict_in_list(ar):
    return base64.encodestring(json.dumps(ar).encode()).decode()


def decode_dict_in_list(ar):
    decode =  base64.b64decode(ar)    
    kps = json.loads(decode)
    return kps
