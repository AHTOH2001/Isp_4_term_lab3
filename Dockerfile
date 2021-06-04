FROM python:3.9

ENV PYTHONUNBUFFERED 1

# VOLUME /home/project
RUN mkdir /home/project

WORKDIR /home/project

COPY requirements.txt /home/project/

RUN pip install --upgrade pip && pip install -r requirements.txt

#CMD pip install -r requirements.txt

# ADD  shop/. /home/project/shop/
ADD  . /home/project/

EXPOSE 8080
