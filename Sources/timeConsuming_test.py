import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('{:}共耗时约 {:.2f} 秒'.format(func,time.time() - start))
        return res
    return wrapper
