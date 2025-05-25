FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -r truser

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY script.sh /app/
RUN chmod +x script.sh

COPY --chown=truser . /app/

ENTRYPOINT [ "/app/script.sh" ]