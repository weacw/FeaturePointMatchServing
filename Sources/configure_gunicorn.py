# configure_gunicorn.py
import os
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

debug = True
loglevel = 'debug'
bind = "0.0.0.0:4530"
pidfile = "log/gunicorn.pid"
accesslog = "log/access.log"
errorlog = "log/debug.log"
daemon = False
preload_app = True
reload = True


# 启动的进程数
workers =  multiprocessing.cpu_count() * 2 +1
worker_class = 'gevent'
threads = 20
x_forwarded_for_header = 'X-FORWARDED-FOR'