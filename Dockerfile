FROM sanicframework/sanic:LTS

RUN mkdir -p /srv
COPY . /srv

WORKDIR /srv

RUN rm -rf proxy_server/vendor
RUN pip3 install -r proxy_server/requirements.txt -t proxy_server/vendor

EXPOSE 9000

ENTRYPOINT ["python3", "proxy_server/app.py"]