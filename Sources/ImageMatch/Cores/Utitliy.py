from flask_restful import reqparse
import werkzeug
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('{:}Total time: {:.5f} s'.format(func, time.time() - start))
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


def get_image_b64(CVAlgorithm,_b64_data):
    return CVAlgorithm.read_base64(_b64_data)
