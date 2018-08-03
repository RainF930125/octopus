FROM centos

ENV HOME=/home/app

RUN yum install -y haproxy python-requests python-netaddr python-jinja2 python-flask python-gunicorn && mkdir -p $HOME && chown -R 1001:0 $HOME

WORKDIR $HOME

COPY app/* ./

USER 1001

EXPOSE 8080

CMD ["/bin/bash", "run.sh"]
