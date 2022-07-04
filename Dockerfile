FROM ubuntu:21.04

ADD main.py .

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install dialog apt-utils -y
RUN apt-get install ffmpeg -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-tk -y
RUN apt-get install python3-pil python3-pil.imagetk -y
RUN pip install opencv-python
RUN pip install tkcalendar
RUN pip install requests
RUN pip install --upgrade psutil
RUN pip3 install yagmail[all]
RUN pip3 install lxml

CMD ["python3", "main.py"]