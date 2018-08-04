FROM centos

ENV HOME=/home/app

RUN yum install -y libnet-devel libpcap-devel

WORKDIR $HOME

COPY arping2 ./
