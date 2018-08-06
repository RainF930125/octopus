FROM centos

ENV HOME=/home/app

RUN yum install -y libnet-devel libpcap-devel python-gunicorn

WORKDIR $HOME

COPY app/* ./

CMD ["/bin/bash", "run.sh"]
