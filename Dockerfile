# Isticmaal Python 3.10.0 base image
FROM python:3.10.0-slim

# Set working directory
WORKDIR /app

# Nuqul file-yada mashruuca
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        flask \
        transformers \
        tensorflow-cpu==2.19.0 \
        sentencepiece \
        requests

# Expose port Flask default
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
