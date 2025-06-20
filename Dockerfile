FROM python:3.10.0-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        flask \
        transformers \
        tensorflow-cpu==2.10.1 \
        sentencepiece \
        requests \
        gdown

EXPOSE 5000

CMD ["python", "app.py"]
