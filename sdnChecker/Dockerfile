FROM centos

RUN yum install -y haproxy python-requests python-netaddr python-jinja2 python-flask nmap-ncat

ENV HOME=/home/app

RUN mkdir -p $HOME

RUN chown -R 1001:0 $HOME

WORKDIR $HOME

COPY haproxy_manager.py .
COPY haproxy.template .
COPY run.py .

USER 1001

EXPOSE 8080

CMD ["python", "run.py"]
