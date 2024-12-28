FROM python:3.9-slim

WORKDIR /app

COPY main.py ./ 
COPY product-service.proto ./ 
COPY proto-compiler.py ./ 

RUN pip install grpcio grpcio-tools prometheus_client psutil
RUN python /app/proto-compiler.py

CMD ["python", "main.py"]
