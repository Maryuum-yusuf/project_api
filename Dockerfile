FROM python:3.10.0-slim

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Install python-dotenv for loading .env
RUN pip install python-dotenv

# Environment variable for Hugging Face
ENV PORT=7860

# Expose port
EXPOSE $PORT

# Start with uvicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
