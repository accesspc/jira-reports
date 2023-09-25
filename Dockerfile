FROM python:3

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

COPY requirements.txt /work/requirements.txt
WORKDIR /work

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "app/main.py", "app/tokens.json" ]
