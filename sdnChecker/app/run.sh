python haproxy_manager.py &
gunicorn -b 0.0.0.0:8080 -w 10 app:application
