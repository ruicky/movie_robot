FROM python:3.8.9-slim
LABEL title="影视剧机器人"
LABEL description="可以自动从豆瓣用户的想看、在看、看过列表中自动获取电影，并通过mteam查找种子，提交到qbittorrent中下载（依赖Emby管理影视原数据）"
LABEL authors="yipengfei"
COPY app /app
COPY yee /app/yee
COPY requirements.txt /app
WORKDIR /app
VOLUME /data
EXPOSE 1329
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive \
    LICENSE_KEY='' \
    PGID=0 \
    PUID=0
RUN apt-get update \
    && apt-get install -y tzdata gcc \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
	&& python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir Cython \
    && python setup_in_docker.py build_ext --inplace \
    && rm -rf setup_in_docker.py requirements.txt\
    && pip uninstall -y Cython \
    && rm -rf /var/lib/apt/lists/*
CMD python /app/start.py -w /data
