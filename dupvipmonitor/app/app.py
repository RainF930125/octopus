#!/usr/bin/python2.7

def app(environ, start_response):
    data = open('./dupvips.dat').read()
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
