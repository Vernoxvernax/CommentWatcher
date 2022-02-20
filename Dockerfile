FROM python:3-slim

RUN useradd -u 911 -U -d /usr/src/app user && \
usermod -G users user
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENTRYPOINT ["./init/init.sh"]
