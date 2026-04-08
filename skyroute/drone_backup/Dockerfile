FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any (e.g., for gymnasiuim)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the standard Hugging Face port
EXPOSE 7860

# Run the persistent API server
CMD ["python", "api.py"]

