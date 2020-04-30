FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get -y install libopenblas-dev gfortran python-numpy python-scipy


COPY ./static /app/static
COPY ./templates /app/templates
COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]