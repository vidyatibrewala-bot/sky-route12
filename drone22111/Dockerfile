FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expect app to run on port 7860
EXPOSE 7860

CMD ["python", "api.py"]
