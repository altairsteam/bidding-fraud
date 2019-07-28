FROM python:3.7.4
ENV PYTHONUNBUFFERED 1
RUN mkdir /detector/
WORKDIR /detector/
COPY ./detector/requirements.txt /detector/
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
RUN pip install -r requirements.txt
COPY . /detector/