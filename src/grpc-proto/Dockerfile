FROM python:3.9-slim

WORKDIR /app

COPY main.py ./ 
COPY product-service.proto ./ 
COPY proto-compiler.py ./ 
COPY database/database.py ./database/database.py
COPY prometheus/metrics.py ./prometheus/metrics.py

RUN pip install grpcio grpcio-tools prometheus_client psutil mysql-connector-python

RUN python /app/proto-compiler.py

CMD ["python", "-u", "main.py"]
