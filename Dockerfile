FROM python:3.5
ENV TZ "Asia/Shanghai"

ADD . /app

WORKDIR /app

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo "deb http://mirrors.163.com/debian/ jessie main non-free contrib" >/etc/apt/sources.list && \
    echo "deb-src http://mirrors.163.com/debian/ jessie main non-free contrib" >>/etc/apt/sources.list

RUN apt-get update -y && apt-get install supervisor -y

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package --no-cache-dir -r deploy/requirements.txt

ENTRYPOINT sed -i 's/\r$//' deploy/entrypoint.sh && bash deploy/entrypoint.sh
