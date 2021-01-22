from flask_restful import reqparse
import werkzeug
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        cost_time='{:} - Total time: {:.5f} ms'.format(
            func.__name__, (time.time() - start)*1000)
        print(cost_time)
        return res
    return wrapper


def get_image(CVAlgorithm, args):
    if args['image_url'] is not None:
        img = CVAlgorithm.url_to_image(args['image_url'])
    elif args['image'] is not None:
        img = CVAlgorithm.bytes_to_image(args['image'])
    else:
        img = CVAlgorithm.read_base64(args['image_base64'])
    return img
