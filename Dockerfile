FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y openssh-client curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service.py .

EXPOSE 5000

CMD ["python", "service.py"]
