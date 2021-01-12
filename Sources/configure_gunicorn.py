# configure_gunicorn.py
import os
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

# debug = True
loglevel = 'debug'
bind = "0.0.0.0:4530"
pidfile = "log/gunicorn.pid"
accesslog = "log/access.log"
errorlog = "log/debug.log"
daemon = False

# 启动的进程数
workers = multiprocessing.cpu_count()
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'