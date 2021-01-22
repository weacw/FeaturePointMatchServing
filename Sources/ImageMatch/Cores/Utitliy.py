from flask_restful import reqparse
import werkzeug
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('{:}Total time: {:.5f} ms'.format(func, (time.time() - start)*1000))
        return res
    return wrapper

@timer
def get_image(CVAlgorithm,args):           
    if args['image_url'] is not None:
        img = CVAlgorithm.url_to_image(args['image_url'])
    elif args['image'] is not None:
        img = CVAlgorithm.bytes_to_image(args['image'])
    return img


def get_image_b64(CVAlgorithm,_b64_data):
    return CVAlgorithm.read_base64(_b64_data)
