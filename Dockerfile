FROM python:3
WORKDIR /xiaomi
COPY xiaomi .
RUN pip install -r /xiaomi/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s usr/local/bin/docker-entrypoint.sh /entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
