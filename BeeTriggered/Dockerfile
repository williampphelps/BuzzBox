FROM python:3.6.1-alpine

RUN pip install --upgrade pip
RUN pip install requests
RUN pip install docker

COPY . . 
CMD ["python", "-u", "main.py"]

