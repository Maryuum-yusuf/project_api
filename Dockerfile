FROM python:3.10.0-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        numpy==1.24.3 \
        flask \
        transformers \
        tensorflow-cpu==2.10.1 \
        sentencepiece \
        gdown

EXPOSE 5000

CMD ["python", "app.py"]
