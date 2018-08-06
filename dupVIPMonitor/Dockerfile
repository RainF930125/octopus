FROM centos

ENV HOME=/home/app

WORKDIR $HOME

RUN yum install -y wget unzip libnet-devel libpcap-devel python-gunicorn && \
    mkdir -p $HOME && \
    wget https://github.com/prometheus/client_python/archive/master.zip && \
    unzip master.zip && \
    cd client_python-master && \
    python setup.py install

COPY app/* ./

CMD ["/bin/bash", "run.sh"]
