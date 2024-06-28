FROM python:3.11.4

COPY . /app

WORKDIR /app

EXPOSE 2222

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]