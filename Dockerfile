FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HF_TOKEN=""
ENV OPENAI_API_KEY=""
ENV API_BASE_URL="https://router.huggingface.co/v1"
ENV MODEL_NAME="gpt-4.1-mini"

CMD ["python", "inference.py"]
