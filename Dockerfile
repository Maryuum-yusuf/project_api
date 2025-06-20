FROM python:3.10.0-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip uninstall -y keras tensorflow && \
    pip install --no-cache-dir \
        tensorflow-cpu==2.10.1 \
        tf-keras \
        flask \
        transformers \
        sentencepiece \
        requests

EXPOSE 5000

CMD ["python", "app.py"]
