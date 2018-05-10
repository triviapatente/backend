import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"
preload_app = True
pidfile = "server_pid.log"
daemon = False
accesslog = "server.log"
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'"
errorlog = "server_errors.log"
