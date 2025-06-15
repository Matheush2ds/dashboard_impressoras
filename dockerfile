FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    iputils-ping \
    snmp \
    libsnmp-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]