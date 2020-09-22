FROM python:3
WORKDIR /xiaomi
COPY ./xiaomi/ /
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python3 main.py"]
