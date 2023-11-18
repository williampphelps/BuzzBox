FROM python:3.8

RUN pip install --upgrade pip
RUN pip install requests
RUN pip install docker

COPY . . 
CMD ["python", "-u", "main.py"]

