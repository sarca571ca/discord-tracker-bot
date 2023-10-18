FROM python:3.9

WORKDIR /app

COPY tools/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
