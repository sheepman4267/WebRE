# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "WebRE.wsgi:application"
# The granularity of Error log outputs
loglevel = "warn"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
try:
    bind = os.environ['GUNICORN_BIND_ADDRESS']
except IndexError:
    print("You didn't specify a bind address and port. Use the environment variable 'GUNICORN_BIND_ADDRESS' with the format '0.0.0.0:8000'.")
    bind = None
    exit(1)
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
accesslog = errorlog = f"/var/log/gunicorn/{os.environ['GUNICORN_PID_LOG_PREFIX']}.log"
# Redirect stdout/stderr to log file
capture_output = False
# PID file so you can easily fetch process ID
pidfile = f"/var/run/gunicorn/{os.environ['GUNICORN_PID_LOG_PREFIX']}.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False
