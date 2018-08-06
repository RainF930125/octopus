FROM centos

ENV HOME=/home/app

WORKDIR $HOME

RUN yum install -y wget unzip haproxy python-requests python-netaddr python-jinja2 python-gunicorn && \
    mkdir -p $HOME && \
    chown -R 1001:0 $HOME && \
    wget https://github.com/prometheus/client_python/archive/master.zip && \
    unzip master.zip && \
    cd client_python-master && \
    python setup.py install

COPY app/* ./

USER 1001

CMD ["/bin/bash", "run.sh"]
