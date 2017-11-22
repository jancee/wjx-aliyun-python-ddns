FROM python:2.7
MAINTAINER Jingxi Wang

# 设置工作空间
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app/

# 将代码复制到该目录并设置为工作空间
COPY . .

RUN pip install requests \
    && chmod +x docker-script/run-per-minute.sh

# 运行程序
CMD ["./docker-script/run-per-minute.sh"]
