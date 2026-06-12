FROM python:3.11-alpine

WORKDIR /app

# Create expected directories
RUN mkdir -p /opt/guardian/logs /app/.state

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY forwarder.py .

CMD ["python", "-u", "forwarder.py"]
